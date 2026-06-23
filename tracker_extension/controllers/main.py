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
                # Try to find extension in the parent directory (if running from e-commerce root)
                parent_dir = os.path.dirname(module_dir)
                extension_path = os.path.join(parent_dir, 'extension')
                if os.path.exists(extension_path):
                    extension_dir = extension_path
            
            if not extension_dir:
                return self._create_extension_from_module(module_dir)
            
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for root, dirs, files in os.walk(extension_dir):
                    # Remove __pycache__ directories from traversal
                    if '__pycache__' in dirs:
                        dirs.remove('__pycache__')
                    
                    for file in files:
                        # Skip system and Python files
                        if file.startswith('.') or file.endswith(('.pyc', '.py', '.pyo')):
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
            
            # Define what to exclude
            EXCLUDED_EXTENSIONS = ('.py', '.pyc', '.pyo')
            EXCLUDED_FILES = {'__init__.py', '__manifest__.py'}
            
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                # First, ensure manifest.json is at the root
                manifest_path = os.path.join(module_dir, 'manifest.json')
                if os.path.exists(manifest_path):
                    zip_file.write(manifest_path, 'manifest.json')
                else:
                    # Try to find manifest in common locations
                    manifest_locations = [
                        os.path.join(module_dir, 'static', 'src', 'extension', 'manifest.json'),
                        os.path.join(module_dir, 'static', 'extension', 'manifest.json'),
                        os.path.join(module_dir, 'extension', 'manifest.json'),
                        os.path.join(os.path.dirname(module_dir), 'extension', 'manifest.json'),
                    ]
                    for loc in manifest_locations:
                        if os.path.exists(loc):
                            zip_file.write(loc, 'manifest.json')
                            break
                
                # Add background.js if exists
                bg_path = os.path.join(module_dir, 'background.js')
                if os.path.exists(bg_path):
                    zip_file.write(bg_path, 'background.js')
                else:
                    # Try parent directory
                    bg_path = os.path.join(os.path.dirname(module_dir), 'extension', 'background.js')
                    if os.path.exists(bg_path):
                        zip_file.write(bg_path, 'background.js')
                
                # Add content.js if exists
                content_path = os.path.join(module_dir, 'content.js')
                if os.path.exists(content_path):
                    zip_file.write(content_path, 'content.js')
                else:
                    content_path = os.path.join(os.path.dirname(module_dir), 'extension', 'content.js')
                    if os.path.exists(content_path):
                        zip_file.write(content_path, 'content.js')
                
                # Helper function to add directory contents
                def add_directory(dir_path, arc_prefix):
                    if not os.path.exists(dir_path):
                        # Try to find in parent/extension folder
                        alt_path = os.path.join(os.path.dirname(module_dir), 'extension', os.path.basename(dir_path))
                        if os.path.exists(alt_path):
                            dir_path = alt_path
                        else:
                            return False
                    
                    for root, dirs, files in os.walk(dir_path):
                        # Skip __pycache__
                        if '__pycache__' in dirs:
                            dirs.remove('__pycache__')
                        
                        for file in files:
                            # Skip excluded files
                            if file.startswith('.') or file in EXCLUDED_FILES:
                                continue
                            if file.endswith(EXCLUDED_EXTENSIONS):
                                continue
                            
                            file_path = os.path.join(root, file)
                            # Preserve subdirectory structure
                            rel_path = os.path.relpath(file_path, dir_path)
                            arcname = os.path.join(arc_prefix, rel_path)
                            zip_file.write(file_path, arcname)
                    
                    return True
                
                # Add popup folder
                popup_dir = os.path.join(module_dir, 'popup')
                if not add_directory(popup_dir, 'popup'):
                    # Fallback: try to find popup files in root
                    popup_files = ['popup.html', 'popup.js', 'popup.css']
                    for file in popup_files:
                        file_path = os.path.join(module_dir, file)
                        if os.path.exists(file_path):
                            zip_file.write(file_path, os.path.join('popup', file))
                
                # Add options folder
                options_dir = os.path.join(module_dir, 'options')
                if not add_directory(options_dir, 'options'):
                    # Fallback: try to find options files in root
                    options_files = ['options.html', 'options.js', 'options.css']
                    for file in options_files:
                        file_path = os.path.join(module_dir, file)
                        if os.path.exists(file_path):
                            zip_file.write(file_path, os.path.join('options', file))
                
                # Add icons folder
                icons_dir = os.path.join(module_dir, 'icons')
                add_directory(icons_dir, 'icons')
                
                # If no files were added, raise an error
                if len(zip_file.namelist()) == 0:
                    raise Exception("No extension files found")
            
            zip_buffer.seek(0)
            return http.send_file(
                zip_buffer,
                filename='tracker-extension.zip',
                as_attachment=True,
                mimetype='application/zip'
            )
        except Exception as e:
            # Return a simple error message
            return http.send_file(
                BytesIO(b"Error creating extension zip: " + str(e).encode()),
                filename='error.txt',
                as_attachment=False,
                mimetype='text/plain'
            )