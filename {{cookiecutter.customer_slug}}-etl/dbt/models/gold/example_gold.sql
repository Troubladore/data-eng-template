-- Example gold model
select source, count(*) as event_count
from {% raw %}{{ ref('example_silver') }}{% endraw %}
group by 1
