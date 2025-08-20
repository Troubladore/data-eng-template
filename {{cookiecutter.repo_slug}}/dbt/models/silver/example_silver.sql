-- Example silver model
select id, source, created_at
from {% raw %}{{ ref('bronze_events') }}{% endraw %}
