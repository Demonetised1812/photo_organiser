from datetime import datetime   
from PIL import Image               
from PIL.ExifTags import TAGS       #used to get metadata from images
from pathlib import Path            #best for working with files and folders instead of os.path
import shutil                       #to copy, move, and manage files
import hashlib                      #to detect duplicates by hashing file contents

desktop_path = Path.home() / "Desktop"
organiser_folder_file_path = desktop_path / "organiserFolder"
image_folder_path = desktop_path / "imageFiles"
jpeg_folder_path = image_folder_path / "jpegFiles"
raw_folder_path = image_folder_path / "rawFiles"
etc_folder_path = image_folder_path / "etcFiles"

def getDate(file) :                                                                             #gets the date and time the photo was taken
    try :
        with Image.open(file) as img :  
            exif = img.getexif()                                                                #stores the exif data in a variable

            for tag_id, value in exif.items() :                                                 #for each key value pairs
                if TAGS.get(tag_id) == "DateTimeOriginal" or TAGS.get(tag_id) == "DateTime":    #checks the metadata for the "DateTimeOriginal" or "DateTime" key depending on what key the image uses
                    date = datetime.strptime(value, "%Y:%m:%d %H:%M:%S")                        #splits the data of value received into individal units and store it in a variable                 
                    return date.strftime("%d-%m-%Y")                                            #returns the useful format of "dd:mm:YYYY" to the user using those seperated units
                
        return None                                                                             #returns none if no metadata values                   
    
    except Exception as e:
        print(file.name, "-> error:", e)
        return None                                                                            #returns none if error occurs

def checkFile(baseFolder, date) :
    if date == None :
        date = "unknown_date"

    target_folder = Path(baseFolder) / date                                                     #creates the file path for target folder
    if target_folder.exists() :                                                                 #check if it exists or not
        return target_folder                                                                    #if yes returns filepath
    else :
        Path(target_folder).mkdir(parents=True, exist_ok=True)                                  #if no create file (including parents if its missing), (parents and exist_ok = true is so that no erros will occur if the folder or file path already exists)
        return target_folder
    
def checkOrganiserDir() :   
    if not organiser_folder_file_path.is_dir() :                                                #checks if the file exists or not
        organiser_folder_file_path.mkdir(parents=True ,exist_ok=True)                           #creates the file and the parent files if it doesnt exist

def checkImageFilesDir() :
    if not image_folder_path.is_dir() :
        image_folder_path.mkdir(parents=True, exist_ok=True)
        jpeg_folder_path.mkdir(parents=True, exist_ok=True)
        raw_folder_path.mkdir(parents=True, exist_ok=True)
        etc_folder_path.mkdir(parents=True, exist_ok=True)

def getHash(file_path) :
    hasher = hashlib.sha256()                                                                   #creates sha 256 object that turns file data into unique fingerprint, gives the hash data
    
    with open (file_path, "rb") as file :                                                       #reads the binary of the file
        while chunk := file.read(8192) :                                                        #reads the file in 8192 byte chunks
            hasher.update(chunk)                                                                #updates chunk as file is being read
        
    return hasher.hexdigest()                                                                   #returns the hex number in 1 readable string

def checkRepeating() : 
    seenHashes = {} 
    number_of_duplicates = 0

    for file in organiser_folder_file_path.iterdir() :
        if not file.is_file() :
            continue

        if file.suffix.lower() in [".jpg", ".jpeg"] :                                           #checks the suffix of the file name to get the file type, lower() to prevent errors from diff capitalisation
            file_path = jpeg_folder_path
        elif file.suffix.lower() == ".nef" :
            file_path = raw_folder_path
        else :
            file_path = etc_folder_path

        file_hash = getHash(file)

        if file_hash in seenHashes :
            number_of_duplicates += 1
            continue
        else : 
            seenHashes[file_hash] = file                                                            #stores the already processed hash values and stores them in a dictionary
            date_taken = getDate(file)                                                              #checks the date the photo was taken
            target_folder = checkFile(file_path, date_taken)                                        #uses the date to see if file path exists
            shutil.move(str(file), str(target_folder))                                                        #moves the files to the targeted file path

    return number_of_duplicates

def main() : 
    checkOrganiserDir()
    checkImageFilesDir()
    num_of_duplicates = checkRepeating()
    print("")
    print("organisation complete")
    print(f"number of duplicate files = {num_of_duplicates}")

if __name__ == "__main__" :
    main()