curl -L -O http://sourceforge.net/projects/pyqt/files/sip/sip-4.16.5/sip-4.16.5.tar.gz
tar -xvf sip-4.16.5.tar.gz
cd sip-4.16.5
python configure.py
make -j 4
sudo make install
cd ..
curl -L -O http://sourceforge.net/projects/pyqt/files/PyQt4/PyQt-4.11.3/PyQt-x11-gpl-4.11.3.tar.gz
tar -xvf PyQt-x11-gpl-4.11.3.tar.gz
cd PyQt-x11-gpl-4.11.3
python configure.py --confirm-license
make -j 4
sudo make install
cd ..