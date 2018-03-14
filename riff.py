from VLC import *
import tkinter as tk
from tkinter import simpledialog
from tkinter import filedialog

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    try:
        from msvcrt import getch
    except ImportError:
        import termios
        import tty

        def getch():  # getchar(), getc(stdin)  #PYCHOK flake
            fd = sys.stdin.fileno()
            old = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                ch = sys.stdin.read(1)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old)
            return ch

    def end_callback(event):
        print('End of media stream (event %s)' % event.type)
        sys.exit(0)

    echo_position = False
    def pos_callback(event, player):
        if echo_position:
            sys.stdout.write('\r%s to %.2f%% (%.2f%%)' % (event.type,
                                                          event.u.new_position * 100,
                                                          player.get_position() * 100))
            sys.stdout.flush()

    def print_version():
        """Print version of this vlc.py and of the libvlc"""
        try:
            print('Build date: %s (%#x)' % (build_date, hex_version()))
            print('LibVLC version: %s (%#x)' % (bytes_to_str(libvlc_get_version()), libvlc_hex_version()))
            print('LibVLC compiler: %s' % bytes_to_str(libvlc_get_compiler()))
            if plugin_path:
                print('Plugin path: %s' % plugin_path)
        except:
            print('Error: %s' % sys.exc_info()[1])

           
    if ( 1 ==1):
        root = tk.Tk()
        root.withdraw()
        movie = filedialog.askopenfilename()
        riff = filedialog.askopenfilename()
        riff = os.path.expanduser(riff)
        movie = os.path.expanduser(movie)
        if not os.access(movie, os.R_OK):
            print('Error: %s file not readable' % movie)
            sys.exit(1)


        # Need --sub-source=marq in order to use marquee below
        instance = Instance(["--sub-source=marq"] + sys.argv[1:])
        try:
            media = instance.media_new(movie)
            riff_audio = instance.media_new(riff)
        except (AttributeError, NameError) as e:
            print('%s: %s (%s %s vs LibVLC %s)' % (e.__class__.__name__, e,
                                                   sys.argv[0], __version__,
                                                   libvlc_get_version()))
            sys.exit(1)
        player = instance.media_player_new()
        player.set_media(media)
        riff_player = instance.media_player_new()
        riff_player.set_media(riff_audio)
        movie_start = simpledialog.askstring("Movie Time", "Enter movie time in 00:00:00 format")
        riff_start = simpledialog.askstring("Riff Time", "Enter Riff time in 00:00:00 format")
        ftr = [3600000,60000,1000]
        movie_start = sum([a*b for a,b in zip(ftr, map(int,movie_start.split(':')))])
        riff_start = sum([a*b for a,b in zip(ftr, map(int,riff_start.split(':')))])
        sync = (riff_start - movie_start)
        player.play()
        riff_player.play()
        player.set_time(movie_start)
        riff_player.set_time(riff_start)
        event_manager = player.event_manager()
        event_manager.event_attach(EventType.MediaPlayerEndReached,      end_callback)
        event_manager.event_attach(EventType.MediaPlayerPositionChanged, pos_callback, player)

        def mspf():
            """Milliseconds per frame"""
            return int(1000 // (player.get_fps() or 25))

        def double_pause():
            player.pause()
            riff_player.pause()


        def print_info():
            """Print information about the media"""
            try:
                media = player.get_media()
                print('State: %s' % player.get_state())
#                print('Media: %s' % bytes_to_str(media.get_mrl()))
 #               print('Track: %s/%s' % (player.video_get_track(), player.video_get_track_count()))
                sec = (player.get_time() / 1000)
                minutes = (sec / 60)
                sec %=60
                hours = (minutes/60)
                minutes %=60
                ctime=(str(hours) + ':' + str(minutes) + ':' + str(sec))
                sec = (media.get_duration() / 1000)
                minutes = (sec / 60)
                sec %=60
                hours = (minutes/60)
                minutes %=60
                dur=(str(hours) + ':' + str(minutes) + ':' + str(sec))

                tmp = ('Current time: %s/%s' % (player.get_time(), media.get_duration()))
                player.video_set_marquee_int(VideoMarqueeOption.Timeout, 5000)
                player.video_set_marquee_int(VideoMarqueeOption.Position, Position.Bottom)
                player.video_set_marquee_string(VideoMarqueeOption.Text, str_to_bytes(ctime+'/'+dur))
                print('Position: %s' % player.get_position())
                print('FPS: %s (%d ms)' % (player.get_fps(), mspf()))
                print('Rate: %s' % player.get_rate())
                print('Video size: %s' % str(player.video_get_size(0)))  # num=0
                print('Scale: %s' % player.video_get_scale())
                print('Aspect ratio: %s' % player.video_get_aspect_ratio())
                print('Window:' % player.get_hwnd())
            except Exception:
                print('Error: %s' % sys.exc_info()[1])

        def sec_forward():
            """Go forward one sec"""
            global sync
            sync =sync+500
            resync()

        def sec_backward():
            """Go backward one sec"""
            global sync
            sync =sync-500
            resync()

        def frame_forward():
            """Go forward one frame"""
            player.set_time(player.get_time() + mspf())

        def frame_backward():
            """Go backward one frame"""
            player.set_time(player.get_time() - mspf())

        def print_help():
            """Print help"""
            print('Single-character commands:')
            for k, m in sorted(keybindings.items()):
                m = (m.__doc__ or m.__name__).splitlines()[0]
                print('  %s: %s.' % (k, m.rstrip('.')))
            print('0-9: go to that fraction of the movie')

        def quit_app():
            """Stop and exit"""
            sys.exit(0)


            
        def resync():
            riff_player.set_time((player.get_time()+sync))
        def movie_volup():
            player.audio_set_volume((player.audio_get_volume())+10)
        def movie_voldown():
            player.audio_set_volume((player.audio_get_volume())-10)
        def riff_volup():
            riff_player.audio_set_volume((riff_player.audio_get_volume())+10)
        def riff_voldown():
            riff_player.audio_set_volume((riff_player.audio_get_volume())-10)



        def forward30():
            player.set_time((player.get_time()+30000))
            riff_player.set_time((riff_player.get_time() + 30000))
#            resync()

        def back30():
            player.set_time((player.get_time() - 30000))
            riff_player.set_time((riff_player.get_time() - 30000))
#            resync()

        def toggle_echo_position():
            """Toggle echoing of media position"""
            global echo_position
            echo_position = not echo_position

        keybindings = {
            ' ': double_pause,
            '+': sec_forward,
            '-': sec_backward,
            '.': frame_forward,
            ',': frame_backward,
            'f': player.toggle_fullscreen,
            'i': print_info,
            'p': toggle_echo_position,
            'q': quit_app,
            '?': print_help,
            'r': resync,
            '>': forward30,
            '<': back30,
            'u': movie_volup,
            'd': movie_voldown,
            'U':riff_volup,
            'D':riff_voldown,
            }

        print('Press q to quit, ? to get help.%s' % os.linesep)
        while True:
            k = getch()
            print('> %s' % k)
            if k in keybindings:
                keybindings[k]()
            elif k.isdigit():
                 # jump to fraction of the movie.
                player.set_position(float('0.'+k))
                resync()

    else:
        print('Usage: %s [options] <movie_filename>' % sys.argv[0])
        print('Once launched, type ? for help.')
        print('')
        print_version()
