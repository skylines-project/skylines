SkyLines systemd setup
===============================================================================

For the production server we are using systemd to start and restart our
services when needed. Instead of running from the `root` user we take advantage
of the "user services" feature of systemd.

This requires that the `skylines` user on the system is allowed to run
long-running services:

    # as root user
    loginctl enable-linger skylines

We also need to allow the [Caddy](http://caddyserver.com/) server to bind to
the HTTP and HTTPS ports:

    # as root user
    setcap 'cap_net_bind_service=+ep' /usr/local/bin/caddy

Finally, we create a symlink from the `systemd` folder of the repository to
`/home/skylines/.config/systemd/user` and then we can start the services using:

    systemctl --user start skylines
    systemctl --user start tracking
    systemctl --user start celery
    systemctl --user start mapproxy
    systemctl --user start caddy


Related
-------------------------------------------------------------------------------

- https://www.brendanlong.com/systemd-user-services-are-amazing.html
- https://github.com/mholt/caddy/tree/v0.11.5/dist/init/linux-systemd
