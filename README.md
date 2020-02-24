# JetAIRace
python3 AICAR.py AnalyzeDataset


python3 AICAR.py LabelVideo -i output.avi


python3 AICAR.py Run


python3 AICAR.py CreateDataset


python3 AICAR.py Train



To start gamepad controller at startup

# sudo cat /etc/systemd/system/JetAIRace_pyscript.service
[Unit]
Description=Execute this gamepadcontroller on boot

[Service]
Type=oneshot
ExecStart=/usr/bin/python3 /home/jetson/JetAIRace/AICAR/manual_control/daemon.py

[Install]
WantedBy=multi-user.target

To enable this at startup
sudo systemctl start JetAIRace_pyscript
sudo systemctl status JetAIRace_pyscript
sudo systemctl enable JetAIRace_pyscript
