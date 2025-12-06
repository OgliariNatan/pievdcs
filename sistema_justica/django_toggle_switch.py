from django.forms.widgets import CheckboxInput
from django.utils.safestring import mark_safe
from django.utils.html import format_html
import json
import uuid


class ToggleSwitchWidget(CheckboxInput):
    """
    A customizable toggle switch widget for Django forms.
    
    Author: Ogliari Natan
    Date: 2025-08-11
    Proposal for Django Foundation
    
    Args:
        size (str): Size of the toggle - 'xs', 'sm', 'md', 'lg', 'xl' or custom tuple (width, height)
        active_color (str): Color when toggle is active (default: '#10B981')
        inactive_color (str): Color when toggle is inactive (default: '#9CA3AF')
        active_text (str): Text to display when active (default: 'Active')
        inactive_text (str): Text to display when inactive (default: 'Inactive')
        show_label (bool): Whether to show the text label (default: True)
        animation_speed (float): Animation speed in seconds (default: 0.3)
    """
    
    # Predefined sizes with maintained proportions
    SIZES = {
        'xs': (32, 16),   # width, height in pixels
        'sm': (40, 20),
        'md': (48, 24),
        'lg': (56, 28),
        'xl': (64, 32),
    }
    
    def __init__(self, size='md', active_color="#9333ea", inactive_color="#0A0A0A",
                 active_text='Active', inactive_text='Inactive', show_label=True,
                 animation_speed=0.3, attrs=None):
        super().__init__(attrs)
        
        # Handle size parameter
        if isinstance(size, str) and size in self.SIZES:
            self.width, self.height = self.SIZES[size]
        elif isinstance(size, (tuple, list)) and len(size) == 2:
            self.width, self.height = size
        else:
            self.width, self.height = self.SIZES['md']
        
        # Calculate proportional dimensions
        self.button_size = int(self.height * 0.75)  # Button is 75% of height
        self.padding = int(self.height * 0.125)      # Padding is 12.5% of height
        self.translate_x = self.width - self.button_size - (self.padding * 2)
        
        # Set colors and text
        self.active_color = active_color
        self.inactive_color = inactive_color
        self.active_text = active_text
        self.inactive_text = inactive_text
        self.show_label = show_label
        self.animation_speed = animation_speed
        
    def render(self, name, value, attrs=None, renderer=None):
        if attrs is None:
            attrs = {}
        
        # Generate unique ID for this instance
        widget_id = attrs.get('id', f'toggle_{uuid.uuid4().hex[:8]}')
        is_checked = bool(value)
        checked_attr = 'checked' if is_checked else ''
        
        # Build the widget HTML
        context = {
            'widget_id': widget_id,
            'name': name,
            'checked': checked_attr,
            'width': self.width,
            'height': self.height,
            'button_size': self.button_size,
            'padding': self.padding,
            'translate_x': self.translate_x,
            'active_color': self.active_color,
            'inactive_color': self.inactive_color,
            'active_text': self.active_text,
            'inactive_text': self.inactive_text,
            'current_text': self.active_text if is_checked else self.inactive_text,
            'current_color': self.active_color if is_checked else self.inactive_color,
            'show_label': 'inline-block' if self.show_label else 'none',
            'animation_speed': self.animation_speed,
            'font_size': max(12, int(self.height * 0.6)),  # Proportional font size
        }
        
        html = '''
        <div class="django-toggle-switch-wrapper" id="wrapper_%(widget_id)s">
            <style>
                #wrapper_%(widget_id)s {
                    display: inline-flex;
                    align-items: center;
                    gap: 8px;
                }
                #wrapper_%(widget_id)s .django-toggle-switch {
                    position: relative;
                    display: inline-block;
                    width: %(width)spx;
                    height: %(height)spx;
                    cursor: pointer;
                }
                #wrapper_%(widget_id)s .django-toggle-switch input {
                    opacity: 0;
                    width: 0;
                    height: 0;
                    position: absolute;
                }
                #wrapper_%(widget_id)s .django-toggle-slider {
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background-color: %(inactive_color)s;
                    transition: background-color %(animation_speed)ss;
                    border-radius: %(height)spx;
                }
                #wrapper_%(widget_id)s .django-toggle-slider:before {
                    position: absolute;
                    content: "";
                    height: %(button_size)spx;
                    width: %(button_size)spx;
                    left: %(padding)spx;
                    bottom: %(padding)spx;
                    background-color: white;
                    transition: transform %(animation_speed)ss;
                    border-radius: 50%%;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
                }
                #wrapper_%(widget_id)s input:checked + .django-toggle-slider {
                    background-color: %(active_color)s;
                }
                #wrapper_%(widget_id)s input:checked + .django-toggle-slider:before {
                    transform: translateX(%(translate_x)spx);
                }
                #wrapper_%(widget_id)s input:focus + .django-toggle-slider {
                    box-shadow: 0 0 0 2px rgba(0,0,0,0.1);
                }
                #wrapper_%(widget_id)s .django-toggle-label {
                    display: %(show_label)s;
                    font-size: %(font_size)spx;
                    user-select: none;
                    transition: color %(animation_speed)ss;
                    color: %(current_color)s;
                }
                
                /* Accessibility improvements */
                #wrapper_%(widget_id)s input:focus-visible + .django-toggle-slider {
                    outline: 2px solid %(active_color)s;
                    outline-offset: 2px;
                }
                
                /* Hover effect */
                #wrapper_%(widget_id)s .django-toggle-switch:hover .django-toggle-slider {
                    opacity: 0.8;
                }
                
                /* Disabled state */
                #wrapper_%(widget_id)s input:disabled + .django-toggle-slider {
                    opacity: 0.5;
                    cursor: not-allowed;
                }
            </style>
            
            <label class="django-toggle-switch" for="%(widget_id)s">
                <input type="checkbox" 
                       name="%(name)s" 
                       id="%(widget_id)s"
                       %(checked)s
                       aria-checked="%(checked)s"
                       aria-label="%(current_text)s"
                       role="switch">
                <span class="django-toggle-slider"></span>
            </label>
            <span class="django-toggle-label" id="%(widget_id)s_label">
                %(current_text)s
            </span>
            
            <script>
                (function() {
                    const toggle = document.getElementById('%(widget_id)s');
                    const label = document.getElementById('%(widget_id)s_label');
                    const config = {
                        activeText: '%(active_text)s',
                        inactiveText: '%(inactive_text)s',
                        activeColor: '%(active_color)s',
                        inactiveColor: '%(inactive_color)s'
                    };
                    
                    if (toggle && label) {
                        toggle.addEventListener('change', function() {
                            if (this.checked) {
                                label.textContent = config.activeText;
                                label.style.color = config.activeColor;
                                this.setAttribute('aria-checked', 'true');
                                this.setAttribute('aria-label', config.activeText);
                            } else {
                                label.textContent = config.inactiveText;
                                label.style.color = config.inactiveColor;
                                this.setAttribute('aria-checked', 'false');
                                this.setAttribute('aria-label', config.inactiveText);
                            }
                        });
                    }
                })();
            </script>
        </div>
        ''' % context
        
        return mark_safe(html)