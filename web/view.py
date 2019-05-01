import json
import logging
import os
from collections import OrderedDict
from glob import glob
from shutil import copyfile

import tornado.web
import tornado.websocket

import forms
import train

from settings import functions, config


def permission(level):
    def _auth(method):
        def wrapper(self, *args, **kwargs):
            if not self.authed(level):
                self.flash_error('Invalid permissions!')
                self.redirect('/')
                raise tornado.web.Finish
            return method(self, *args, **kwargs)
        return wrapper
    return _auth


class BaseHandler(tornado.web.RequestHandler):
    def __init__(self, *args, **kwargs):
        super(BaseHandler, self).__init__(*args, **kwargs)

        # default values
        self.tmpl = {
            'meta': {
                'description': 'A recognition system for your team.',
                'keywords': 'detect, recognise, facial, detection, team, id, recogniser, id my team, idmy.team'
            },
            'error_message': self.get_secure_cookie('error_message'),
            'success_message': self.get_secure_cookie('success_message'),
            'member': json.loads(self.get_secure_cookie('member') or '{}'),
            'authed': self.authed,
            'socket_status': config.SOCKET_STATUS,
            'socket_connected': config.SOCKET_STATUS == config.SOCKET_CONNECTED
        }

        # remove flash messages
        self.set_secure_cookie('error_message', '')
        self.set_secure_cookie('success_message', '')

    def flash_error(self, message, redirect_url=''):
        self.set_secure_cookie('error_message', message)
        if redirect_url:
            return self.redirect(redirect_url)

    def flash_success(self, message, redirect_url=''):
        self.set_secure_cookie('success_message', message)
        if redirect_url:
            return self.redirect(redirect_url)

    def check_xsrf_cookie(self):
        pass

    def authed(self, perm):
        """
        :param perm: the level requested
        :return: whether allowed
        """

        level = 'low'
        for l in config.PERMISSIONS:
            if int(self.tmpl['member']['perm']) == config.PERMISSIONS[l]['level']:
                level = l

        return config.PERMISSIONS[level]['level'] >= config.PERMISSIONS[perm]['level']

    def db_connect(self):
        return functions.connect(config.DB["username"], config.DB["password"], config.DB["db"])

    def display_chart(self, html_id, labels, sets, y_label, point_radius=0):
        if isinstance(labels, int):
            labels = "new Array(" + str(labels) + ")"

        return """
        <script>
        $(document).ready(function(){{
            new Chart(document.getElementById("{id}"), {{
                "type": "line",
                "data": {{
                    labels: {labels},
                    datasets: [{sets}]
                }},
                "options": {{
                    scales: {{
                        xAxes: [{{
                            display: '{x_axes}',
                            gridLines: {{
                                display:false
                            }}
                        }}],
                        yAxes: [{{
                            drawBorder: false,
                            scaleLabel: {{
                                display: true,
                                labelString: "{y_label}"
                            }}
                        }}]
                    }},
                    elements: {{ point: {{ radius: '{r}' }} }} // remove data points
                }}
            }});
        }});
        </script>
        """.format(id=html_id, labels=labels, sets=sets, x_axes='true' if labels else 'false',
                   y_label=y_label, r=point_radius)

    def get_face_cookies(self):
        return functions.unescape(self.get_cookie('face-coordinates'))


class Error404(BaseHandler):
    def get(self):
        self.write('404')


class WelcomeHandler(BaseHandler):
    def get(self):
        self.tmpl['title'] = ''
        self.render('home/welcome.html', **self.tmpl)


class ClassifyHandler(BaseHandler):
    @permission('medium')
    def get(self):
        self.tmpl['title'] = 'Classify'

        conn = self.db_connect()
        self.tmpl['images'] = ClassifyImagesHandler.get_images(conn, self.get_face_cookies(), True)
        self.tmpl['members'] = MembersHandler.get_members(conn)

        self.render('classify.html', **self.tmpl)

    @permission('medium')
    def post(self):
        img_paths = self.request.arguments['paths']
        names = self.request.arguments['names']

        cookie_faces = self.get_face_cookies()
        conn = self.db_connect()
        classify_cnt = 0
        for i in range(len(img_paths)):
            img_path = img_paths[i].decode()
            member_id = functions.Member.name_to_id(conn, names[i].decode())
            if member_id > 0:
                if img_path in cookie_faces:
                    functions.Image.Comment.write(img_path, cookie_faces[img_path])
                elif not functions.Image.Comment.read(img_path):
                    self.flash_error('Image contains no facial coordinates!', '/classify')

                # move image to classification directory
                file_name = os.path.basename(img_path)
                os.rename(img_path, config.CLASSIFIED_PATH + str(member_id) + '/' + file_name)
                classify_cnt += 1

        self.flash_success('Success! Classified {} images.'.format(classify_cnt))
        self.redirect('/classify')


class ClassifyImagesHandler(BaseHandler):
    @permission('medium')
    def get(self, classifying):
        self.tmpl['images'] = self.get_images(self.db_connect(), self.get_face_cookies(), classifying)
        self.tmpl['classifying'] = classifying
        self.render('helpers/classify-images.html', **self.tmpl)

    @classmethod
    def get_images(cls, conn, face_coordinates, classifying=False, img_paths=False):
        if img_paths == False:
            # file paths
            img_paths = glob(config.UNCLASSIFIED_PATH + "*" + config.IMG_TYPE)
            if not classifying:
                img_paths.extend(glob(config.CLASSIFIED_PATH + "*" + config.IMG_TYPE))

        img_paths.sort(key=lambda x: os.path.getmtime(x))  # sort image paths by creation date

        images = OrderedDict()
        for img_path in img_paths:
            file_name = os.path.basename(img_path)

            if face_coordinates and img_path in face_coordinates:
                coordinate = face_coordinates[img_path]
            else:
                coordinate = functions.Image.Comment.read(img_path)

            try:
                coordinate = coordinate.decode()
            except AttributeError:
                pass

            member_id = ''
            member_name = ''
            if '_' in file_name:
                member_id = file_name.split("_")[0]
                name = functions.Member.id_to_name(conn, member_id)
                if name != functions.Member.UNKNOWN_NAME:
                    member_name = name

            images[img_path] = {
                'img': functions.Image.base_64_src(img_path),
                'coordinates': coordinate,
                'type': '' if config.TMP_CLASSIFIED_PATH in img_path else 'classified',
                'member_id': member_id,
                'member_name': member_name
            }

        return images


class MemberHandler(BaseHandler):
    @permission('low')
    def get(self, member_id):
        conn = self.db_connect()
        self.tmpl['member'] = functions.Member.get_by_member_id(conn, member_id)
        self.tmpl['title'] = self.tmpl['member']['name']

        # member activity
        member_activity = functions.Member.get_activity(conn, member_id)
        recognitions = [rec['score'] for rec in member_activity if rec['type'] == 'RECOGNISED']
        self.tmpl['num_recognitions'] = len(recognitions)
        self.tmpl['num_trained'] = functions.Member.get_num_trained(conn, member_id)
        set = """{{
            label: 'Recognition Scores',
            data: [{data}],
            borderWidth: 1,
            borderColor: '#333',
            fill: false
        }}""".format(data=','.join(str(s) for s in recognitions))
        self.tmpl['chartjs'] = self.display_chart('scores', self.tmpl['num_recognitions'], set, "Scores",
                                                  point_radius=2)

        self.render('member.html', **self.tmpl)


class MemberPasswordHandler(BaseHandler):
    @permission('high')
    def get(self, member_id):
        self.tmpl['form'] = forms.NewMemberPasswordForm()
        user = functions.Member.get_by_member_id(self.db_connect(), member_id)['name']
        self._screen(user)

    @permission('high')
    def post(self, member_id):
        self.tmpl['form'] = form = forms.NewMemberPasswordForm(self.request.arguments)
        conn = self.db_connect()
        user = functions.Member.get_by_member_id(conn, member_id)['name']
        if form.validate():
            password = form.password.data
            if functions.Member.set_pw(conn, member_id, password):
                self.flash_success('Success updating the password of %s!' % (user,), '/members')
            else:
                self.flash_error('Error updating password of %s!' % (user,), '/members')
        self._screen(user)

    def _screen(self, user):
        self.tmpl['title'] = 'Change %s password' % (user,)
        self.render('helpers/form.html', **self.tmpl)


class MembersHandler(BaseHandler):
    @permission('low')
    def get(self):
        self._screen()

    def _screen(self):
        self.tmpl['title'] = "Members"

        conn = self.db_connect()
        self.tmpl['min_training_images'] = config.MIN_TRAINING_IMAGES_PER_MEMBER
        self.tmpl['permissions'] = config.PERMISSIONS
        self.tmpl['face_css'] = self._face_css
        self.tmpl['members'] = self.get_members(conn)
        _, self.tmpl['train_allowed'], _ = train.allowed()

        self.render('members.html', **self.tmpl)

    def _face_css(self, percentage, colour1, colour2):
        return """
        background: -moz-linear-gradient(bottom, {colour2} 0%, {colour2} {percentage}, {colour1} {percentage}, {colour1} 100%);
        background: -webkit-linear-gradient(bottom, {colour2} 0%, {colour2} {percentage}, {colour1} {percentage}, {colour1} 100%);
        background: linear-gradient(to top, {colour2} 0%, {colour2} {percentage}, {colour1} {percentage}, {colour1} 100%);
        filter: progid:DXImageTransform.Microsoft.gradient( startColorstr={colour2}, endColorstr={colour1}, GradientType=0);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        """.format(percentage=percentage, colour1=colour1, colour2=colour2)

    @staticmethod
    def get_member_info(conn, id):
        member = {}
        member['num_trained'] = functions.Member.get_num_trained(conn, id)
        member['num_to_train'] = len(glob(config.CLASSIFIED_PATH + str(id) + '/*'))
        return member

    @staticmethod
    def get_members(conn):
        members = []
        for member in functions.Member.get_all(conn):
            member.update(MembersHandler.get_member_info(conn, member['id']))
            members.append(member)
        return members


class MemberTrainHandler(BaseHandler):
    @permission('high')
    def get(self, member_id):
        self._screen(self.db_connect(), member_id)

    @permission('high')
    def post(self, member_id):
        conn = self.db_connect()

        # create classified member directory
        classified_dir = config.CLASSIFIED_PATH + member_id
        if not os.path.isdir(classified_dir):
            os.mkdir(classified_dir)

        face_coordinates = self.get_face_cookies()

        # verify number of new images
        valid_img_cnt = 0
        img_paths = self.request.arguments['paths']
        for img_path in img_paths:
            img_path = img_path.decode()
            logging.info(img_path)
            if img_path not in face_coordinates and not functions.Image.Comment.read(img_path):
                self.tmpl['error_message'] = 'Not added coordinates for every image'
                return self._screen(conn, member_id)
            else:
                valid_img_cnt += 1

        if valid_img_cnt < config.MIN_TRAINING_IMAGES_PER_MEMBER:
            self.tmpl['error_message'] = 'You must add at least {} images'.format(config.MIN_TRAINING_IMAGES_PER_MEMBER)
            return self._screen(conn, member_id)

        # write face coordinates to files and move to classified directory
        for img_path in img_paths:
            img_path = img_path.decode()
            face_coord = face_coordinates.pop(img_path, None)
            if face_coord:
                functions.Image.Comment.write(img_path, face_coord)
                file_name = img_path.replace(config.TMP_CLASSIFIED_PATH + member_id, '')
                os.rename(img_path, classified_dir+file_name)
        self.set_cookie('face-coordinates', functions.escape(face_coordinates))

        # zip directory
        message, success = train.upload(conn)
        if success:
            self.tmpl['success_message'] = message
        else:
            self.tmpl['error_message'] = 'Training Error: ' + message
        self._screen(conn, member_id)

    def _screen(self, conn, member_id):
        self.tmpl['title'] = 'Training Images'

        self.tmpl['team_member'] = functions.Member.get_by_member_id(conn, member_id)
        self.tmpl['team_member'].update(MembersHandler.get_member_info(conn, member_id))

        img_paths = glob(config.CLASSIFIED_PATH + member_id + '/*')
        img_paths.extend(glob(config.TMP_CLASSIFIED_PATH + member_id + '/*'))

        self.tmpl['images'] = ClassifyImagesHandler.get_images(self.db_connect(), self.get_face_cookies(), img_paths=img_paths)
        self.tmpl['min_training_images'] = config.MIN_TRAINING_IMAGES_PER_MEMBER

        self.tmpl['camera_running'] = bool(int(config.settings["Camera"]['Run']['val']))
        self.tmpl['silent_mode'] = bool(int(config.settings["Camera"]['Silent Mode']['val']))
        self.tmpl['live_stream'] = bool(int(config.settings['Camera']['Live Stream']['val']))
        self.tmpl['mask'] = bool(int(config.settings['Camera']['Mask']['val']))
        self.tmpl['recurring_time'] = config.settings["Training"]["Recurring Time"]["val"]
        self.render('train.html', **self.tmpl)


class AddMemberHandler(BaseHandler):
    @permission('high')
    def get(self):
        self.tmpl['form'] = forms.NewMemberForm()
        self._screen()

    @permission('high')
    def post(self):
        self.tmpl['form'] = form = forms.NewMemberForm(self.request.arguments)
        if not form.validate():
            return self._screen()

        member_id = functions.Member.add(self.db_connect(), form.name.data, form.password.data, form.permission.data)
        if not member_id:
            return self.redirect("/")

        return self.redirect('/member/' + str(member_id) + '/train')

    def _screen(self):
        self.tmpl['title'] = "Add Team Member"
        self.tmpl['include_scripts'] = ['js/add-member.js']
        self.render('helpers/form.html', **self.tmpl)


class LiveStreamHandler(BaseHandler):
    @permission('low')
    def get(self):
        self.tmpl['title'] = "Stream"
        self.tmpl['camera_running'] = bool(int(config.settings["Camera"]['Run']['val']))
        self.tmpl['live_stream'] = bool(int(config.settings['Camera']['Live Stream']['val']))
        self.render('stream.html', **self.tmpl)


class StreamCaptureHandler(BaseHandler):
    @permission('medium')
    def post(self, member_id):
        dir = config.TMP_CLASSIFIED_PATH + member_id + "/"
        save_path = functions.random_file_name(dir, config.IMG_TYPE)

        if not os.path.isdir(dir):
            os.mkdir(dir)

        copyfile(config.TMP_IMG_PATH, save_path)
        self.redirect("/member/" + member_id + "/train#livestream")


class StreamCaptureDeleteHandler(BaseHandler):
    @permission('medium')
    def post(self, member_id):
        img_path = self.get_argument('image_path')
        if functions.path_in_dir(img_path, config.TMP_CLASSIFIED_PATH) or functions.path_in_dir(img_path, config.CLASSIFIED_PATH):
            # valid img file path to delete
            try:
                os.remove(img_path)
            except FileNotFoundError:
                pass

            return self.redirect("/member/" + member_id + "/train#images")
        self.flash_error('Problem deleting training image!', "/member/" + member_id + '/train')


class SettingsHandler(BaseHandler):
    @permission('high')
    def get(self):
        self.tmpl['title'] = 'Settings'
        self.tmpl['settings'] = config.settings
        self._store_stats()
        self.tmpl['stats'] = config.stats
        self.tmpl['stats_info'] = config.STATS_INFO
        self.render('settings.html', **self.tmpl)

    @permission('high')
    def post(self):
        restart_camera = False
        for key in self.request.arguments:
            split = key.split("_")
            type = split[0].replace("-", " ").title()
            setting = split[1].replace("-", " ").title()

            val = self.get_argument(key)
            val = val if 'on' not in val else 1
            # convert val to int if possible
            try:
                val = int(val)
            except:
                pass

            if config.settings[type][setting]['val'] != val:
                # value changed
                config.settings[type][setting]['val'] = val
                if setting in config.CAMERA_RESTART_SETTINGS:
                    restart_camera = True
        if restart_camera:
            config.RESTART_CAMERA = True
        functions.YAML.write(config.SETTINGS_FILE, config.settings)
        self.redirect('/settings')

    def _store_stats(self):
        # storage
        st = os.statvfs("/")
        total_storage = functions.to_GB(st.f_bsize * st.f_blocks)
        storage_left = functions.to_GB(st.f_bavail * st.f_frsize)
        config.stats[config.STAT_STORAGE] = str(storage_left) + "/" + str(total_storage) + " GB"

        # number of classified
        config.stats[config.STAT_NUM_CLASSIFIED] = functions.num_files_in_dir(
            config.ROOT_DIR + config.settings["File Location"]['Classified Images']['val'])

        # number of unclassified
        config.stats[config.STAT_NUM_UNCLASSIFIED] = functions.num_files_in_dir(
            config.ROOT_DIR + config.settings["File Location"]['Unclassified Images']['val'])

        config.stats[config.STAT_CPU_TEMP] = functions.get_cpu_temp()

class ScriptHandler(BaseHandler):
    @permission('medium')
    def get(self):
        self.tmpl['file_content'] = open(config.SCRIPT_PATH, 'r').read()
        self._screen()

    def _screen(self):
        self.tmpl['title'] = 'Script'
        self.tmpl['script_speed'] = '0.002'
        self.render('script.html', **self.tmpl)

    @permission('high')
    def post(self):
        bash_script_content = self.get_argument('bash-script')
        error_message = functions.Shell.validate(bash_script_content, config.SCRIPT_PATH)
        if error_message:
            self.tmpl['error_message'] = "<pre>" + error_message + "</pre>"
        self.tmpl['file_content'] = bash_script_content
        self._screen()


class LogsHandler(BaseHandler):
    @permission('high')
    def get(self, page=1, level=2):

        self.tmpl['title'] = 'Logs'

        conn = self.db_connect()
        self.tmpl['page'] = int(page)
        self.tmpl['page_size'] = 30
        self.tmpl['logs'] = functions.Logs.get_logs(conn, self.tmpl['page'], self.tmpl['page_size'], level) or {}
        self.tmpl['logging_levels'] = logging._levelToName
        self.tmpl['current_level'] = int(level)

        if self.tmpl['current_level'] not in logging._levelToName:
            self.tmpl['current_level'] = logging.NOTSET

        self.render('logs.html', **self.tmpl)


class LogsDeleteHandler(BaseHandler):
    @permission('high')
    def get(self):
        conn = self.db_connect()
        functions.Logs.purge(conn)
        self.redirect('/logs')
