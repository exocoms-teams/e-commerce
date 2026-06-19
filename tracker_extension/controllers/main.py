from odoo import http
from odoo.http import request
import os
import zipfile
from io import BytesIO

class TrackerExtensionController(http.Controller):

    @http.route('/tracker-extension', type='http', auth='public', website=True)
    def extension_page(self):
        """Display the extension download page"""
        return request.render('tracker_extension.extension_download_page')

    @http.route('/tracker-extension/download', type='http', auth='public')
    def download_extension(self):
        """Serve the extension as a zip file"""
        extension_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'src', 'extension')
        
        if not os.path.exists(extension_dir):
            return request.not_found()
        
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for root, dirs, files in os.walk(extension_dir):
                for file in files:
                    if file.endswith('.pyc') or file.startswith('.'):
                        continue
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, extension_dir)
                    zip_file.write(file_path, arcname)
        
        zip_buffer.seek(0)
        
        return http.send_file(
            zip_buffer,
            filename='tracker-extension.zip',
            as_attachment=True,
            mimetype='application/zip'
        )