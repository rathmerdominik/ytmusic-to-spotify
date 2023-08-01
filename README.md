### YTMusic Likes to Spotify Saved Tracks converter

I needed a quick way to transfer my YouTube Music likes over to Spotify as there is no official Linux YouTube music client and the third party ones are just painful to use as they are laggy and full of errors.

This script ports all of your Youtube Music likes over to Spotify. There is no need to create a file or put your credentials in a config file. Everything will be done over OAuth and Terminal questions.

The script will generate 4 files when it is done:  
The `error.log` file contains all the errors that occur during the run  
The `duplicate.log` file contains all tracks where duplicates have been found during runtime  
The `not_found.log` file contains all tracks where no corresponding track on Spotify could be found. Please search for these manually  
The `added.log` file contains all found and converted tracks

### IMPORTANT

By default the script clears out your entire Spotify Library to have a clean starting base. This behaviour can be disabled by setting the constant `CLEANUP_FIRST` inside the code to False.

If you have a lot of missing entries you can try to set the `DIRTY_SEARCH_ON_MULTIPLE` constant to True. This can have varying quality results though! 

If you want the program to always take the first matching entry on multiple found matches then you can set `USER_CHOICE_ON_MULTIPLE` to False