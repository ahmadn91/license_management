# -*- coding: utf-8 -*-
# from odoo import http


# class LicenseManagement(http.Controller):
#     @http.route('/license_management/license_management/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/license_management/license_management/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('license_management.listing', {
#             'root': '/license_management/license_management',
#             'objects': http.request.env['license_management.license_management'].search([]),
#         })

#     @http.route('/license_management/license_management/objects/<model("license_management.license_management"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('license_management.object', {
#             'object': obj
#         })
