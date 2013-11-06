sysctl { "net.ipv4.ip_forward": value => "1" }

group { "puppet":
  ensure => "present",
}

File { owner => 0, group => 0, mode => 0644 }

openvpn::server { "ovpn":
  country      => "BE",
  province     => "BRU",
  city         => "Brussels",
  organization => "secaas.be",
  email        => "mini.pelle@gmail.com",
  server       => "10.200.200.0 255.255.255.0",
  proto        => "tcp",
  push         => ["redirect-gateway"],
  local        => ""
}

resources { "firewall":
  purge => true
}

firewall {"100 snat ovpn traffic":
    chain    => "POSTROUTING",
    jump     => "MASQUERADE",
    proto    => "all",
    outiface => "eth0",
    source   => "0.0.0.0/0",
    table    => "nat"
}

openvpn::client { "client1":
    server   => "ovpn",
    remote_host => "%(remote_host)s",
    port => "1194",
    proto => "tcp"
}
