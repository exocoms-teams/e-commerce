odoo.define('your_module_name.extension_dashboard', function (require) {
    "use strict";

    var publicWidget = require('web.public.widget');
    var core = require('web.core');
    var _t = core._t;

    var ThemeToggle = publicWidget.Widget.extend({
        selector: '.o_theme_toggle_widget',
        events: {
            'click': '_onToggleTheme',
        },
        _onToggleTheme: function () {
            var currentTheme = document.documentElement.getAttribute('data-theme');
            if (currentTheme === 'dark') {
                document.documentElement.setAttribute('data-theme', 'light');
                localStorage.setItem('theme', 'light');
                this.$el.find('.theme-icon').text('🌙');
            } else {
                document.documentElement.setAttribute('data-theme', 'dark');
                localStorage.setItem('theme', 'dark');
                this.$el.find('.theme-icon').text('☀️');
            }
        },
        start: function () {
            var savedTheme = localStorage.getItem('theme') || 'light';
            document.documentElement.setAttribute('data-theme', savedTheme);
            if (savedTheme === 'dark') {
                this.$el.find('.theme-icon').text('☀️');
            } else {
                this.$el.find('.theme-icon').text('🌙');
            }
            return this._super.apply(this, arguments);
        }
    });

    var LanguageToggle = publicWidget.Widget.extend({
        selector: '.o_lang_toggle_widget',
        events: {
            'change': '_onLanguageChange',
        },
        _onLanguageChange: function () {
            var lang = this.$el.val();
            window.location = '/lang/' + lang;
        },
    });

    publicWidget.registry.themeToggle = ThemeToggle;
    publicWidget.registry.langToggle = LanguageToggle;

    return {
        ThemeToggle: ThemeToggle,
        LanguageToggle: LanguageToggle,
    };
});