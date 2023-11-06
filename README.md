# Total

<hr>

## - Setup Python venv

## - Install requirements from txt file

```sh
sudo chmod -R 777 *
pip3 install -r requirements.txt
sudo chmod -R 775 *
```

## - See what packages are installed

pip3 list

<hr>

## Run app

```sh
cd /web/TotalLogistixIntegration

# activate env
source tlx/bin/activate

# run script for orders ready to ship
python3 tlxrun.py import -s ready
# shipment
python3 tlxrun.py import -s ship
# daily shipment
# deferred
# parcel
python3 tlxrun.py import -s parcel

# run script to get orders
python3 tlxrun.py export

# close env
deactivate
```

# Run manual files

```sh
scp filename.csv <user>@<host>:/path-to-project-root/.
# add filename to file_list variable in ftp_ops.py
# run script
```

# Local FTP for testing on macbook

- create another user from settings for ftp use
- settings > General > Sharing > Turn on Remote Login
- click info icon and 'Allow full disk access for remote users' for FTP user
- create a folder in your Downloads folder
- TODO forgot how to allow access for FTP

NOTE: Turn off Remote Login when done
