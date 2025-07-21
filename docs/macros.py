"""
Simplified Macros for MkDocs
"""

def define_env(env):
    """
    Define macros and filters for MkDocs
    """
    
    @env.macro
    def grid(columns='auto', gap='md'):
        """
        Create a responsive grid layout
        Usage: {{ grid(columns=3, gap='lg') }}
        """
        if columns == 'auto':
            grid_class = "grid grid--auto-fit"
        else:
            grid_class = f"grid grid--{columns}"
        
        if gap and gap != 'md':
            grid_class += f" grid--gap-{gap}"
        
        return f'<div class="{grid_class}">'
    
    @env.macro
    def endgrid():
        """Close a grid layout"""
        return '</div>'
    
    @env.macro
    def card(type='default', title=None, content=None, link=None):
        """
        Create a card component
        Usage: {{ card(type='feature', title='My Feature', content='Description', link='#') }}
        """
        card_class = f"c-card c-card--{type}"
        
        html = f'<div class="{card_class}">'
        
        if title:
            html += f'<h3 class="c-card__title">{title}</h3>'
        
        if content:
            html += f'<div class="c-card__body">{content}</div>'
        
        if link:
            html += f'<a href="{link}" class="c-card__link">Learn more →</a>'
        
        html += '</div>'
        
        return html

def on_pre_page_macros(env):
    """
    Called before processing macros on a page
    """
    pass

def on_post_page_macros(env):
    """
    Called after processing macros on a page
    """
    pass

def on_post_build(env):
    """
    Called after the build is complete
    """
    pass