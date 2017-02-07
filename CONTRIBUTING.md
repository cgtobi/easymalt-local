How to help adding new institutions
===================================

Is your institution providing an OFX URL we can easily connect to?  
Check if it is listed [here](http://www.ofxhome.com/index.php/home/directory/all).
If it is, nice! Just [open an issue](https://github.com/gboudreau/easymalt-local/issues), and let us know the details.

If your institution doesn't provide an OFX URL, things are much more complicated! :(

The following procedure will create a HTTP dump of you connecting to your financial institution, and downloading transactions information.  
You will need to edit this to remove your credentials (username, password, ...) and share the resulting dump with a EasyMalt developer __privately__.  

If you are not comfortable sharing your downloaded information with a developer, you can try to create the Downloader & Importer yourself (you will need to code in Python to do so).

- Install [Charles](https://www.charlesproxy.com/)
- [Setup SSL proxying](https://www.charlesproxy.com/documentation/proxying/ssl-proxying/)
- Start recording in Charles
- In your browser, open a new incognito tab
- Go to your financial institution website, login, and download either OFX (preferred) or tab-separated files for all your accounts.
- If you are connecting to a credit card provider, make sure you download files for at least the current and previous billing cycle.
- In Charles, stop recording, and save the result.
- Use Cmd-F (Ctrl-F) to find all the requests that contain your credentials (username, password, security answers, etc.)  
  Edit those (right-click them choose _Compose_, and edit the new line. Replace your sensitive data with placeholders like _myusernanehere_.  
  Delete the old line (the one that still contain your credentials).

Zip the resulting .chls file, and send it to guillaume@pommepause.com  
You might also want to [open an issue](https://github.com/gboudreau/easymalt-local/issues) to keep track of things. __Dont__ attach your Charles dump to the issue; you probably don't want the whole world to see your financial transactions!
