#zetaboards-backup

##What is it?

A Python-based project utilising Django (the web framework) and Scrapy (the web
scraping framework) to backup a forum hosted at Zetaboards the semi-hard way, by 
automatically accessing all forums and threads and scraping the data.

##Why on earth would you do that?

Because after hosting a forum with Zetaboards for over 6 years (both on their
free and premium packages), it came time to move elsewhere and they refused to
provide a backup of data held with them.

##What it does back up.

* Members (with basic profile stats e.g post count)
* Forums
* Threads
* Posts (raw bbcode, not just html)

##What it does not back up.

It was written to fit my specific use case and will therefore most likely not
fit yours. The following could be fixed by adding to the spider.

* Non-normal threads (stickies, closed, moved etc)
* Polls
* Calendar data
* Member bits (signatures, avatars, advanced profile info)

##How do you use it?

I do not recommend trying to use this without extensive knowledge of Python,
Django & Scrapy; it will almost certainly not work out of the box on your
install and will require a bit of a rewrite to get working how you wish. 
Because of that I will only give a few starting pointers:

* You will need to copy the Django settings_local.py.dist to settings_local.py
  and set that up appropriately.
* You will need to copy the Scrapy scraper/settings_local.py.dist to
  scraper/settings_local.py and set that up appropriately.
* The command 'scrapy crawl zetaboards' will run the spider.

##General workflow:

All data is stored in a custom model structure due to not having access to
their actual schema.

* Spider logs in as a user of the forum (account should have admin rights)
* It then hits the main category page (forum index) and gets all
  categories/forums, creating new Scrapy requests and passing the forums to the
  pipeline.
* It then hits the topic list views (for each forum) and passes topics to the
  pipeline while also generating the extra requests to view the topics. This
  does support pagination.
* Then it hits the topics to get the posts. This also handles topic pagination.
* During all of these, if it finds a username that does not exist, it will look
  up their profile URL to get the details it requires.
* At the very end, there is a Scrapy signal set to link up the User's generated
  to the topics and posts they own.
* After this, you will need to manually run a Django management command to
  export from the custom model structure to however you want the SQL to look
  after. This follows a pluggable structure and therefore you should be able to
  write your own exporter, there is already one included for exporting to
  Invision Power Board 3.1 and has worked succesfully. (python manage.py sql_export)
* There is also a Django management command lying around which searches all posts for
  links to images and downloads them; this was merely an added extra and isn't
  really part of the backup procedude. (python manage.py download_images)

**You use this software completely AT YOUR OWN RISK, I accept NO LIABILITY from the
use of this software.**
