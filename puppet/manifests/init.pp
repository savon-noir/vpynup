sysctl::directive {
  "net.ipv4.ip_forward": value => 1;
}

group { "puppet":
  ensure => "present",
}

File { owner => 0, group => 0, mode => 0644 }

openvpn::client { 'client1':
    server => 'ovpn',
    proto  => 'tcp',
    port => '1194'
}

openvpn::server { 'ovpn':
  country      => "BE",
  province     => "BRU",
  city         => "Brussels",
  organization => "secaas.be",
  email        => "mini.pelle@gmail.com",
  server       => '10.200.200.0 255.255.255.0',
  proto        => 'tcp',
  local        => ''
}
