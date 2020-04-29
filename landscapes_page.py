import os, sys

landPage = '/home/bret/servers/repo-skylinesC/skylinesC/ember/app/templates/landscapes.hbs'
dir = '/media/sf_landscapes-zip'
dirlist = os.listdir(dir)
names = []
sizes = []
for item in dirlist:
    if '.torrent' in item:
        name = item.split('.torrent')[0]
        names.append(name)
        sizes.append (os.stat('{}/{}'.format(dir,name)).st_size)
print names

lines = []
lines.append('<BasePage> \n')

lines.append('  <div class="page-header"> \n')
lines.append('    <h1>{{t "landscapes"}}</h1> \n')
lines.append('  </div> \n')
lines.append('  <p> {{t "landscapes-download"}} </p> \n')
lines.append('  <p> {{t "install"}} <a href="https://www.fosshub.com/qBittorrent.html">  {{"qBittorrent"}}</a> {{t "qbittorent"}} {{t "torrent"}} </p> \n')
lines.append('  <hr> \n')

lines.append('<table class="table table-striped"> \n')
lines.append('  <thead> \n')
lines.append('        <th class="column-buttons"> {{t "name"}}</th> \n')
lines.append('        <th class="column-buttons"></th> \n')
lines.append('        <th class="column-buttons"></th> \n')
lines.append('  </thead> \n')

lines.append('  <tbody> \n')

for i, name in enumerate(names):
    lines.append('\t<tr> \n')
    lines.append('\t\t<td> {{"' + name + '"}} </td> \n')
    sizeStr = '{:.1f} GB"'.format(sizes[i] /float(10 ** 9))
    lines.append('\t\t<td align = "right"> {{"' + sizeStr  + '}} </td> \n')
    # lines.append('\t\t<td> <a href="http://199.192.98.227:8080/landscapes-zip/{}" download>'.format(name) + ' {{fa-icon "download" size="sm"}} HTTP </a> </td> \n')
    lines.append('\t\t<td> <a href="http://199.192.98.227:8080/landscapes-zip/{}.torrent" download>'.format(name) + ' {{fa-icon "download" size="sm"}} Torrent </a> </td> \n')
    lines.append('\t</tr> \n\n')

lines.append('  </tbody> \n')
lines.append(' </table> \n')

lines.append('</BasePage> \n')

file = open(landPage, 'w')
file.writelines(lines)
file.close()
