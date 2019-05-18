import os

import train
import view
from settings import functions, config


class LogoutHandler(view.BaseHandler):
    def get(self):
        self.clear_all_cookies()
        self.redirect("/")


class MemberDeleteHandler(view.BaseHandler):
    @view.permission("high")
    def get(self, member_id):
        if self.tmpl["member"]["id"] == member_id:
            self.flash_error("You cannot remove yourself!", "/members")

        if not functions.Member.remove(
            self.db_connect(), member_id, config.CLASSIFIED_PATH
        ):
            self.flash_error("Error removing member!", "/members")

        return self.redirect("/members")


class MemberPermHandler(view.BaseHandler):
    @view.permission("high")
    def post(self, member_id):
        permission = int(self.get_argument("perm"))

        if member_id in (0, self.tmpl["member"]["id"]):  # 0 = root member id
            return self.write_error(502)

        valid_perm = False
        for p in config.PERMISSIONS:
            if permission == config.PERMISSIONS[p]["level"]:
                valid_perm = True
                break

        if not valid_perm:
            return self.write_error(503)

        if not functions.Member.set_permission(
            self.db_connect(), member_id, permission
        ):
            return self.write_error(504)


class MembersTrainHandler(view.BaseHandler):
    @view.permission("high")
    def get(self):
        conn = self.db_connect()
        message, success = train.upload(conn)
        if success:
            self.flash_success(message, "/members")
        else:
            self.flash_error(message, "/members")


class ClassifyHandler(view.BaseHandler):
    @view.permission("medium")
    def post(self):
        for img_path in self.request.arguments["image_paths[]"]:
            img_path = img_path.decode("utf-8")
            if functions.path_in_dir(
                img_path, config.UNCLASSIFIED_PATH
            ) and os.path.isfile(img_path):
                os.remove(img_path)


class ClassifyDeleteHandler(view.BaseHandler):
    @view.permission("medium")
    def post(self):
        for img_path in self.request.arguments["image_paths[]"]:
            img_path = img_path.decode("utf-8")
            if functions.path_in_dir(
                img_path, config.UNCLASSIFIED_PATH
            ) and os.path.isfile(img_path):
                os.remove(img_path)


class StreamHandler(view.BaseHandler):
    @view.permission("medium")
    def get(self):
        self.set_header("Content-Type", "image/jpeg")
        if os.path.isfile(config.TMP_IMG_PATH):
            self.write(open(config.TMP_IMG_PATH, "rb").read())
        else:
            self.write("No file")


class FaceCoordinatesHandler(view.BaseHandler):
    @view.permission("medium")
    def post(self):
        face_coordinates = functions.unescape(self.get_cookie("face-coordinates"))
        face_coordinates[self.get_argument("img_path")] = self.get_argument("coords")
        self.set_cookie("face-coordinates", functions.escape(face_coordinates))


class RetractHandler(view.BaseHandler):
    def get(self):
        if (
            self.get_argument("key")
            == config.settings["Retract Recognition"]["Time"]["val"]
        ):
            functions.incorrect_classification(
                conn=self.application.db.connect(),
                ws=config.ws,
                capture_time=int(config.settings["Retract Recognition"]["Time"]["val"]),
                tmp_dir=config.TMP_DETECTED_DIR,
                unclassified_dir=config.UNCLASSIFIED_PATH,
            )
