 <h1 align="center">YTMusic Likes to Spotify Saved Tracks converter </h1>

I needed a quick way to transfer my YouTube Music likes over to Spotify as there is no official Linux YouTube music client and the third party ones are just painful to use as they are laggy and full of errors.

This script ports all of your Youtube Music likes over to Spotify. There is no need to create a file or put your credentials in a config file. Everything will be done over OAuth and Terminal questions.

<h2>Logs</h2>
The script will generate 4 files when it is done:  

<strong>The `error.log` file contains all the errors that occur during the run
The `duplicate.log` file contains all tracks where duplicates have been found during runtime  
The `not_found.log` file contains all tracks where no corresponding track on Spotify could be found. Please search for these manually  
The `added.log` file contains all found and converted tracks
</strong>
<h2>Options</h2>

`-c` Will wipe all saved tracks you have from spotify to offer a clean base for syncing

`-d` Will do a dirty search to find a matching spotify track for youtube music tracks where no match could be found

`-u` Will allow the user to choose what to do when multiple spotify tracks have been matched on one youtube music track
