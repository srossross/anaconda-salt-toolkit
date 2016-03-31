# init.sls


{% set data = salt['pillar.get']('profile:data:redis:port', 'No Data') %}

echo "Hello {{data}}":
  cmd.run

echo "Goodbye {{data}}":
  cmd.run

