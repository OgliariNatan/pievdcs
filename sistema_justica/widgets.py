from django.forms.widgets import CheckboxInput
from django.utils.safestring import mark_safe

class ToggleSwitchWidget(CheckboxInput):
    """Widget de Toggle Switch simples e funcional"""
    
    def render(self, name, value, attrs=None, renderer=None):
        if attrs is None:
            attrs = {}
        
        widget_id = attrs.get('id', f'id_{name}')
        is_checked = bool(value)
        checked = 'checked' if is_checked else ''
        label_text = 'Solicitada' if is_checked else 'Não Solicitada'
        label_color = '#9333ea' if is_checked else '#6B7280'
        
        html = f'''
        <div class="toggle-switch-wrapper">
            <style>
                .toggle-switch-wrapper {{
                    display: inline-block;
                }}
                .toggle-switch {{
                    position: relative;
                    display: inline-block;
                    width: 44px;
                    height: 22px;
                }}
                .toggle-switch input {{
                    opacity: 0;
                    width: 0;
                    height: 0;
                }}
                .toggle-slider {{
                    position: absolute;
                    cursor: pointer;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background-color: #ccc;
                    transition: .3s;
                    border-radius: 22px;
                }}
                .toggle-slider:before {{
                    position: absolute;
                    content: "";
                    height: 16px;
                    width: 16px;
                    left: 3px;
                    bottom: 3px;
                    background-color: white;
                    transition: .3s;
                    border-radius: 50%;
                }}
                input:checked + .toggle-slider {{
                    background-color: #9333ea;
                }}
                input:checked + .toggle-slider:before {{
                    transform: translateX(22px);
                }}
                .toggle-label {{
                    margin-left: 8px;
                    vertical-align: middle;
                    font-size: 14px;
                    font-weight: {"600" if is_checked else "normal"};
                    color: {label_color};
                }}
            </style>
            
            <label class="toggle-switch">
                <input type="checkbox" 
                       name="{name}" 
                       id="{widget_id}"
                       {checked}>
                <span class="toggle-slider"></span>
            </label>
            <span class="toggle-label" id="{widget_id}_label">
                {label_text}
            </span>
            
            <script>
                (function() {{
                    var toggle = document.getElementById('{widget_id}');
                    if (toggle) {{
                        toggle.addEventListener('change', function() {{
                            var label = document.getElementById('{widget_id}_label');
                            if (this.checked) {{
                                label.textContent = 'Solicitada';
                                label.style.color = '#9333ea';
                                label.style.fontWeight = '600';
                            }} else {{
                                label.textContent = 'Não Solicitada';
                                label.style.color = '#6B7280';
                                label.style.fontWeight = 'normal';
                            }}
                        }});
                    }}
                }})();
            </script>
        </div>
        '''
        
        return mark_safe(html)