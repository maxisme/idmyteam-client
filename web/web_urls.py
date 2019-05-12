import view, events, authed

www_urls = [
    (r'/', view.WelcomeHandler),
    (r'/login', authed.LoginHandler),
    (r'/logout', authed.LogoutHandler),


    (r'/settings', view.SettingsHandler),
    (r'/script', view.ScriptHandler),
    (r'/logs', view.LogsHandler),
    (r'/logs/(\d+)', view.LogsHandler),
    (r'/logs/(\d+)/(\d+)', view.LogsHandler),
    (r'/logs/delete', view.LogsDeleteHandler),

    (r'/live-stream', view.LiveStreamHandler),
    (r'/stream', events.StreamHandler),

    (r'/classify', view.ClassifyHandler),
    (r'/classify/delete', events.ClassifyDeleteHandler),
    (r'/classify/set-face-coordinates', events.FaceCoordinatesHandler),

    (r'/members', view.MembersHandler),
    (r'/members/train', events.MembersTrainHandler),

    (r'/member/(\d+)', view.MemberHandler),
    (r'/member/add', view.AddMemberHandler),
    (r'/member/(\d+)/train', view.MemberTrainHandler),
    (r'/member/(\d+)/password', view.MemberPasswordHandler),
    (r'/member/(\d+)/delete', events.MemberDeleteHandler),
    (r'/member/(\d+)/permission', events.MemberPermHandler),
    (r'/member/(\d+)/capture', view.StreamCaptureHandler),
    (r'/member/(\d+)/capture/delete', view.StreamCaptureDeleteHandler),

    (r'/retract', events.RetractHandler)
]