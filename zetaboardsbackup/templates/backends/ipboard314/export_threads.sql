INSERT INTO `ipb_topics` (`tid`, `title`, `description`, `state`, `posts`, `starter_id`, `start_date`, `last_poster_id`, `last_post`, `icon_id`, `starter_name`, `last_poster_name`, `poll_state`, `last_vote`, `views`, `forum_id`, `approved`, `author_mode`, `pinned`, `moved_to`, `topic_hasattach`, `topic_firstpost`, `topic_queuedposts`, `topic_open_time`, `topic_close_time`, `topic_rating_total`, `topic_rating_hits`, `title_seo`, `seo_last_name`, `seo_first_name`, `topic_deleted_posts`) VALUES

{% for thread in threads %}
({{ thread.zeta_id }}, '{{ thread.title }}', '{{ thread.subtitle|default:"" }}', 'open', 0, {{ thread.user.zeta_id }}, {{ thread.date_posted|date:"U" }}, NULL, NULL, 0, '{{ thread.username }}', '', '0', 0, {{ thread.views }}, {{ thread.forum.zeta_id }}, 1, 0, 0, '0', 0, 1, 0, 0, 0, 3, 1, '{{ thread.title|slugify }}', '', '{{ thread.username|slugify }}', 0){% if not forloop.last %},{% else %};{% endif %}
{% endfor %}

