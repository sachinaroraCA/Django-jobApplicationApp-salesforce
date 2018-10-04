from main_app.Constants.designation_drivefolder_mapping import BASE_FOLDER
from main_app.utils.drive_api import GoogleDrive


def get_folder_id(folder_name, parent_folder='TEST'):
    """
    :param folder_name:
    :param parent_folder:
    :return:
    """
    from main_app.Constants.designation_drivefolder_mapping import FOLDER
    if folder_name in FOLDER.folder_id.keys():
        return True, FOLDER.folder_id[folder_name]
    else:
        from main_app.Constants.designation_drivefolder_mapping import PARENT_FOLDER
        service = GoogleDrive()
        if parent_folder in PARENT_FOLDER.folder_id.keys():
            
            folder_id = service.create_folder(folder_name=folder_name,
                                              parent_folder=PARENT_FOLDER.folder_id[parent_folder])

            added_entry = add_entry_of_folder('FOLDER', folder_name, folder_id)

            if not added_entry:
                print("File permission Error")
                return False, "FOLDER file entry not added due to file permissions"
            else:
                return True, folder_id
        else:
            if BASE_FOLDER.folder_id:
                parent_folder_id = service.create_folder(folder_name=parent_folder,
                                                         parent_folder=BASE_FOLDER.folder_id)

                added_entry = add_entry_of_folder('PARENT_FOLDER', parent_folder, parent_folder_id)
                if not added_entry:
                    print("File permission Error")
                    return False, "PARENT_FOLDER file entry not added due to file permissions"
                else:
                    get_folder_id(folder_name, parent_folder)
            else:
                return False, "Google drive base folder does not exists"


def add_entry_of_folder(folder_type, folder_name, folder_id):
    """
    :param folder_type:
    :param folder_name:
    :param folder_id:
    :return:
    """
    import os

    # Build paths inside the project like this: os.path.join(BASE_DIR, ...)
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    file_path = BASE_DIR + '/Constants/designation_drivefolder_mapping/{folder_type}.py'.format(
                            folder_type=folder_type)

    file_content = "\nfolder_id.update({'"+ folder_name + "': '" + folder_id + "'})"

    with open("{file_path}".format(file_path=file_path), "a") as f:
        if f.writable():
            f.write("{content}".format(content=file_content))
            f.close()
            success = True
        else:
            success = False
    return success
