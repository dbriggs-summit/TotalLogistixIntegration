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