import os, sys

landPage = '/home/bret/servers/repo-skylinesC/skylinesC/ember/app/templates/landscapes.hbs'
dir = '/media/sf_landscapes-zip'
dirlist = os.listdir(dir)
names = []
sizes = []
for item in dirlist:
    if '.torrent' in item:
        names.append(item.split('.torrent')[0])
        sizes.append (os.stat('{}/{}'.format(dir,item)).st_size)

print names

lines = []
lines.append('<BasePage> \n')

lines.append('  <div class="page-header"> \n')
lines.append('    <h1>{{t "landscapes"}}</h1> \n')
lines.append('  </div> \n')
lines.append('  <p> {{t "landscapes-download"}} </p> \n')
lines.append('  <p> {{t "landscapes-extract"}} </p> \n')
lines.append('  <hr> \n')
lines.append('  <p> <a href="https://www.fosshub.com/qBittorrent.html"> {{"qBittorrent "}}</a> {{t "torrent"}} </p> \n')
lines.append('  <hr> \n')

lines.append('<table class="table table-striped"> \n')
lines.append('  <thead> \n')
lines.append('        <th class="column-buttons"> {{t "name"}}</th> \n')
lines.append('        <th class="column-buttons"></th> \n')
lines.append('        <th class="column-buttons"></th> \n')
lines.append('  </thead> \n')

lines.append(' <tbody> \n')

for i, name in enumerate(names):
    lines.append('<tr> \n')
    lines.append('<td> {{' + name + '}} </td> \n')
    lines.append('<td> {{' + '{:.1f} MB'.format(sizes[i] / float(10 ** 6))  + '}} </td> \n')
    lines.append('<td> <a href = "http://199.192.98.227:8080/landscapes-zip/Temuco_Los_Andes.7z" download> {{fa - icon "download" size = "sm"}} HTTP </ a> </td> \n')
    lines.append('<td> <a href = "http://199.192.98.227:8080/landscapes-zip/Temuco_Los_Andes.7z.torrent" download> {{fa - icon "download" size = "sm"}} Torrent </ a> </td> \n')
    lines.append('</tr> \n')



lines.append('  </tbody> \n')
lines.append(' </table> \n')

lines.append('</BasePage> \n')

file = open(landPage, 'w')
file.writelines(lines)
file.close()
