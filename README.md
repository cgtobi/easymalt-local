Local Finances Downloader & Importer
====================================

Download transactions information from your financial institutions' websites, and import them in a MySQL database.  
Will also post-process those transactions in order to renamed, categorize and/or tag them per your preference.

Requirements
------------

- Python 3.x and [virtualenv](https://virtualenv.pypa.io) installed.  
The latest macOS version (Sierra) already has the necessary Python 3.5 & virtualenv requirements installed.  
- You will also need a recent PHP version installed: `brew install php71`

Installation
------------

1. Install the python requirements (in a virtual environment):
    ```
    $ virtualenv --python=python3 venv
    $ source venv/bin/activate
    (venv) $ easy_install ofxclient
    (venv) $ sed -i'' -e 's/ofxdata.read()/ofxdata.read().encode()/' venv/lib/python*/site-packages/ofxclient-*-py*.egg/ofxclient/cli.py
    (venv) $ pip install requests
    (venv) $ pip install keyring
    (venv) $ echo "`pwd`" > $(python -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")/maltease.pth
    ```

2. If some of your institutions provides access to your data using an OFX URL (search for your institutions on [ofxhome.com](http://ofxhome.com/) to know), configure `ofxclient` for your institutions, run:
    ```
    $ venv/bin/ofxclient --config .local_config/ofxclient-tangerine.ini
    ```

Replacing `.local_config/ofxclient-tangerine.ini` with a different filename for each of your institutions.

3. Install [composer](https://getcomposer.org/), and run it from the project directory:

    ```
    $ cd /path/to/finances-local/
    $ composer install
    ```

4. Copy `config.example.php` to `config.php`, and change the configuration options in that file.

5. Create the (remote or local) database to save the data into.

    ```
    mysql > CREATE DATABASE 'finances_local' CHARACTER SET = 'utf8mb4';
    mysql > GRANT SELECT, UPDATE, INSERT ON 'finances'.* to 'loc_fin_user'@'localhost' identified by 'some_password_here';
    mysql > source path/to/_dbschema/schema.sql
    ```
    
Change the `tags` column in `transactions` and `post_processing` tables to the tags you'd like to use.  
Add or change the example post-processing rules from the `post_processing` table as needed.  
Change the available categories in the `categories` tables.

6. If you want to receive reports by email, make sure your computer can send emails from the command line. Test it with:

    ```
    $ echo "test" | mail -s Test1 you@gmail.com
    ```
    
7. Install the launchd configuration:

    ```
    $ sudo ln -s /path/to/finances-local/bin/download-n-import.sh /usr/local/bin/
    $ cd ~/Library/LaunchAgents/
    $ ln -s /path/to/finances-local/launchd/com.pommepause.finances.local.plist
    $ launchctl load -w com.pommepause.finances.local.plist
    ```
    
Every day at 10am, launchd will execute `/usr/local/bin/download-n-import.sh`, which will download then import your data into your configured database.  
If configured, you will receive an email report when this process completes.
