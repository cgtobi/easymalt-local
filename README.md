Easy mint Alternative: Local Downloader & Importer
==================================================

Download transactions information from your financial institutions' websites, and import them in a local SQLite database.  
If configured, will also send the downloaded accounts and transactions to a remote web service, for further post-processing and to feed a web-app, like [EasyMalt](https://github.com/gboudreau/easymalt).


Supported institutions
----------------------
See [this folder](https://github.com/gboudreau/easymalt-local/tree/master/easymalt/downloaders/) for a list of all the supported institutions.  
There are not that many right now. :|

See [CONTRIBUTING.md](https://github.com/gboudreau/easymalt-local/tree/master/) if you'd like to help add new institutions.


Requirements
------------

- Python 3.x and [virtualenv](https://virtualenv.pypa.io)  
The latest macOS version (Sierra) already has the necessary Python 3.5 & virtualenv requirements installed.  

Installation
------------

1. Install the python requirements (in a virtual environment):
    ```
    $ virtualenv --python=python3 venv
    $ source venv/bin/activate
    (venv) $ easy_install ofxclient
    (venv) $ sed -i'' -e 's/ofxdata.read()/ofxdata.read().encode()/' venv/lib/python*/site-packages/ofxclient-*-py*.egg/ofxclient/cli.py
    (venv) $ pip install ofxparse
    (venv) $ pip install requests
    (venv) $ pip install keyring
    (venv) $ echo "`pwd`" > $(python -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")/easymalt.pth
    ```

2. Copy `easymalt.example.ini` to `easymalt.ini` and edit as required.

3. Configure all the selected institutions by running the downloader manually once:
    ```
    $ source venv/bin/activate
    (venv) $ python easymalt/cron.py
    ```

4. If you want to receive reports by email, make sure your computer can send emails from the command line. Test it with:
    ```
    $ echo "test" | mail -s Test1 you@gmail.com
    ```
    
5. Mac only: Install the launchd configuration:
    ```
    $ sudo ln -s `pwd`/bin/download-n-import.sh /usr/local/bin/
    $ ln -s `pwd`/launchd/com.pommepause.easymalt.local.plist ~/Library/LaunchAgents/
    $ launchctl load -w ~/Library/LaunchAgents/com.pommepause.easymalt.local.plist
    ```
    
Every day at 10am, launchd will execute `/usr/local/bin/download-n-import.sh`, which will download then import your data, and optionally send all downloaded information to your remote web-app.  
If configured, you will receive an email report when this process completes.

If you are not on Mac, you will need to execute the _bin/download-n-import.sh_ script yourself (manually or automatically).
