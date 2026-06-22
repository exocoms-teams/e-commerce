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
        try:
            # Get the module directory
            module_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
            # Try multiple possible paths for the extension directory
            possible_paths = [
                os.path.join(module_dir, 'static', 'src', 'extension'),
                os.path.join(module_dir, 'static', 'extension'),
                os.path.join(module_dir, 'extension'),
            ]
            
            extension_dir = None
            for path in possible_paths:
                if os.path.exists(path):
                    extension_dir = path
                    break
            
            if not extension_dir:
                # Create a minimal extension zip from the files in the module
                return self._create_extension_from_module(module_dir)
            
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
        except Exception as e:
            return request.not_found()

    def _create_extension_from_module(self, module_dir):
        """Create extension zip from source files if extension directory doesn't exist"""
        try:
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                # Add root extension files
                root_files = [
                    'manifest.json',
                    'background.js',
                    'content.js',
                ]
                
                for file in root_files:
                    file_path = os.path.join(module_dir, file)
                    if os.path.exists(file_path):
                        zip_file.write(file_path, file)
                
                # Add popup folder
                popup_dir = os.path.join(module_dir, 'popup')
                if os.path.exists(popup_dir):
                    for root, dirs, files in os.walk(popup_dir):
                        for file in files:
                            if file.startswith('.'):
                                continue
                            file_path = os.path.join(root, file)
                            arcname = os.path.join('popup', file)
                            zip_file.write(file_path, arcname)
                else:
                    # Fallback: try to find popup files in root
                    popup_files = ['popup.html', 'popup.js', 'popup.css']
                    for file in popup_files:
                        file_path = os.path.join(module_dir, file)
                        if os.path.exists(file_path):
                            zip_file.write(file_path, os.path.join('popup', file))
                
                # Add options folder
                options_dir = os.path.join(module_dir, 'options')
                if os.path.exists(options_dir):
                    for root, dirs, files in os.walk(options_dir):
                        for file in files:
                            if file.startswith('.'):
                                continue
                            file_path = os.path.join(root, file)
                            arcname = os.path.join('options', file)
                            zip_file.write(file_path, arcname)
                else:
                    # Fallback: try to find options files in root
                    options_files = ['options.html', 'options.js', 'options.css']
                    for file in options_files:
                        file_path = os.path.join(module_dir, file)
                        if os.path.exists(file_path):
                            zip_file.write(file_path, os.path.join('options', file))
                
                # Add icons folder
                icons_dir = os.path.join(module_dir, 'icons')
                if os.path.exists(icons_dir):
                    for root, dirs, files in os.walk(icons_dir):
                        for file in files:
                            if file.startswith('.'):
                                continue
                            file_path = os.path.join(root, file)
                            arcname = os.path.join('icons', file)
                            zip_file.write(file_path, arcname)
            
            zip_buffer.seek(0)
            return http.send_file(
                zip_buffer,
                filename='tracker-extension.zip',
                as_attachment=True,
                mimetype='application/zip'
            )
        except Exception as e:
            raise e