"""Main executable. Imports the monox script and causes execution."""
from uart_wifi.scripts import monox

print(f'this should be executed from "{monox.__file__}".')
