(function () {
    'use strict';
    document.addEventListener('DOMContentLoaded', function () {
        var boxes = document.querySelectorAll('.o_spec_facet');
        if (!boxes.length) { return; }

        function applyFilters() {
            var grouped = {};
            document.querySelectorAll('.o_spec_facet:checked').forEach(function (cb) {
                var aid = cb.dataset.attrId;
                if (!grouped[aid]) { grouped[aid] = []; }
                grouped[aid].push(cb.dataset.value);
            });
            var params = new URLSearchParams();
            Object.keys(grouped).forEach(function (aid) {
                params.set('spec_' + aid, grouped[aid].join(','));
            });
            var cat = new URLSearchParams(window.location.search).get('category');
            if (cat) { params.set('category', cat); }
            window.location.href = '/shop/spec-filter?' + params.toString();
        }

        boxes.forEach(function (cb) {
            cb.addEventListener('change', applyFilters);
        });
    });
})();
