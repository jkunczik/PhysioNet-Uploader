from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException, TimeoutException
import os, time
from logger import get_logger
import lxml.html
import configargparse

logger = get_logger(__name__)

def open_session(project_id, username, password):
    driver = webdriver.Firefox()
    driver.get(f"https://physionet.org/projects/{project_id}/files/")

    try:
        driver.find_element(By.XPATH, '//*[@id="id_username"]').send_keys(username)
        driver.find_element(By.XPATH, '//*[@id="id_password"]').send_keys(password)
        driver.find_element(By.XPATH, '//*[@id="id_remember"]').click()
        driver.find_element(By.XPATH, '//*[@id="login"]').click()
    except:
        logger.info("Existing session. No login necessarry")
    return driver

def upload_dir(driver, dir):
    logger.info(f"Uploading: {dir}")
    # 1. Inspect source dir
    # =====================
    items = os.listdir(dir)
    files = []
    folders = []
    for item in items:
        item_path = os.path.join(dir, item)
        if os.path.isfile(item_path):
            files.append(item_path)
        elif item not in [".", ".."]:
            folders.append(item_path)

    # 2. Upload files
    # ===============
    if len(files) > 0 :
        # Filter files that are already present
        # -------------------------------------
        filtered_items = []
        file_names = [os.path.basename(x) for x in files]
        dir_name = os.path.dirname(files[0])

        time.sleep(0.5)
        root = lxml.html.fromstring(driver.page_source)
        for item in root.xpath('//table[@class="files-panel"]/tbody/tr/td[1]/a'):
            item_name = item.text
            if item_name in file_names:
                files.remove(os.path.join(dir_name, item_name))
                filtered_items.append(item_name)

        if len(filtered_items) > 0:
            logger.info(f"The following files were already present and won't be uploaded again: {', '.join(filtered_items)}")

        # Upload all other files
        # ----------------------
        batch_size = 500
        for i in range(0, len(files), batch_size):
            upload_files(driver, files[i:(i+batch_size)])

    # 3. Add subfolders
    # =================
    for folder in folders:
        add_folder(driver, folder)
        upload_dir(driver, folder)

    # 4. Go back to parent folder
    # ===========================
    leave_folder(driver)

def remove_all(driver):
    time.sleep(0.5)
    items = driver.find_elements(By.XPATH, '//table[@class="files-panel"]/tbody/tr/td[4]/input')
    for item in items:
        item.click()

def add_folder(driver, dir):
    dir_name = os.path.basename(dir)

    create_folder(driver, dir_name)
    enter_folder(driver, dir_name)

def create_folder(driver, dir_name):
    # Return if Folder is already present
    # ===================================
    time.sleep(0.5)
    root = lxml.html.fromstring(driver.page_source)
    for item in root.xpath('//table[@class="files-panel"]/tbody/tr[@class="subdir"]/td[1]/a'):
        item_name = item.text
        if item_name == dir_name:
            logger.info(f"Folder '{dir_name}' already exists. Skipping creation.")
            return

    # Else create it
    # ==============
    try:
        wait_for_element_to_be_clickable(driver, (By.ID, 'create-folder-button'))
        driver.find_element(By.XPATH, '//*[@id="create-folder-button"]').click()
        wait_for_element_to_be_clickable(driver, (By.ID, 'create-folder-button-submit'))
        driver.find_element(By.XPATH, '//*[@id="id_folder_name"]').send_keys(dir_name)
        driver.find_element(By.XPATH, '//*[@id="create-folder-button-submit"]').click()
    except TimeoutException:
        driver.refresh()
        create_folder(driver, dir_name)

def enter_folder(driver, dir_name):
    try:
        items = driver.find_elements(By.XPATH, '//table[@class="files-panel"]/tbody/tr[@class="subdir"]/td[1]/a')
        for item in items:
            if item.get_attribute('innerHTML') == dir_name:
                item.click()
                wait_for_element_to_be_clickable(driver, (By.ID, 'create-folder-button'))
                wait_for_element_to_be_clickable(driver, (By.ID, 'upload-files-button'))
                break
    except TimeoutException:
        driver.refresh()
        enter_folder(driver, dir_name)

def leave_folder(driver):
    try:
        driver.find_element(By.CLASS_NAME, 'parentdir').find_element(By.XPATH, './/td[1]/a').click()
        wait_for_element_to_be_clickable(driver, (By.ID, 'create-folder-button'))
        wait_for_element_to_be_clickable(driver, (By.ID, 'upload-files-button'))
    except TimeoutException:
        driver.refresh()
        leave_folder(driver)

def upload_files(driver, files):
    files_str = "\n".join(files)

    try:
        wait_for_element_to_be_clickable(driver, (By.ID, 'upload-files-button'))
        driver.find_element(By.XPATH, '//*[@id="upload-files-button"]').click()
        wait_for_element_to_be_clickable(driver, (By.ID, 'upload-files-button-submit'))
        driver.find_element(By.XPATH, '//*[@id="id_file_field"]').send_keys(files_str)
        driver.find_element(By.XPATH, '//*[@id="upload-files-button-submit"]').click()
        wait_for_element_to_be_gone(driver, (By.ID, 'upload-files-modal'))
    except TimeoutException:
        driver.refresh()
        upload_files(driver, files)

def wait_for_element_to_be_clickable(driver, el):
    wait_for_element(driver, EC.element_to_be_clickable(el))

def wait_for_element_to_be_gone(driver, el):
    wait_for_element(driver, EC.invisibility_of_element_located(el))

def wait_for_element(driver, condition):
    ignored_exceptions= (NoSuchElementException,StaleElementReferenceException,)
    WebDriverWait(driver,10,ignored_exceptions=ignored_exceptions).until(condition)

if __name__ == "__main__":
    parser = configargparse.ArgParser(
        description='Programmatically upload a dataset to PhysioNet. Requires Firefox.',
        default_config_files=['*.yaml', '*.conf']
    )
        
    
    # Credentials
    # ===========
    parser.add('--ProjectID', help='The ID of the Physionet Project. Can be found in a brwoser by accessing your ' + \
                                   'project page and extracting it from the URL ' + \
                                   '("https://physionet.org/projects/\{ProjecID\})', required=True)
    parser.add('--Username', help='Your PhysioNet username', required=True)
    parser.add('--Password', help='Your PhysioNet password', required=True)

    # Configuation
    # ============
    parser.add('--DatsetDir', help='The directory on your local machine containing the dataset.', required=True)

    config = parser.parse_args()

    driver = open_session(config.ProjectID, config.Username, config.Password)
    upload_dir(driver, config.DatsetDir)