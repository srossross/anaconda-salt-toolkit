# init.sls


{% set data = salt['pillar.get']('profile:data:redis:port', 'No Data') %}

hello:
  cmd.run:
    - name: mecho "Hello {{data}}"

echo "Goodbye {{data}}":
  cmd.run

