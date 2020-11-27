
import config
import os, sys
def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dj.settings')
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv+['runserver',f'{config.HOST}:{config.PORT}'])
if __name__ == '__main__':
    main()
