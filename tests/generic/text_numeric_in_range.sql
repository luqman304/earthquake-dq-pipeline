{#-
    Generic test for raw VARCHAR columns. Fails on any value that is
      * not parseable as a number, or
      * outside [min_value, max_value].
    Empty values are ignored (pair with not_null where a value is required).
-#}
{% test text_numeric_in_range(model, column_name, min_value, max_value) %}

select {{ column_name }} as raw_value
from {{ model }}
where {{ column_name }} is not null
  and (
        try_cast({{ column_name }} as double) is null
     or try_cast({{ column_name }} as double) < {{ min_value }}
     or try_cast({{ column_name }} as double) > {{ max_value }}
  )

{% endtest %}
