from flask import Flask, request, send_file, render_template, jsonify
import yt_dlp
import os
import uuid
import threading
import time
import mimetypes

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get_formats', methods=['POST'])
def get_formats():
    url = request.form['url']
    formats = []

    try:
        with yt_dlp.YoutubeDL({
            'quiet': True,
            'skip_download': True,
            'no_warnings': True,
            'cookiefile': 'cookies.txt'

        }) as ydl:
            info = ydl.extract_info(url, download=False)
            seen = set()
            for f in info.get('formats', []):
                if (
                    f.get('ext') == 'mp4' and 
                    f.get('height') and 
                    isinstance(f.get('height'), int)
                ):
                    res = f['height']
                    if res in [144, 240, 360, 480, 720, 1080, 1440, 2160] and res not in seen:
                        size = round((f.get('filesize', 0) or 0) / 1024 / 1024, 1)
                        label = f"{res}p"
                        if size > 0:
                            label += f" ({size} MB)"
                        formats.append({
                            'format_id': res,  # now sending height instead of format_id
                            'label': label
                        })
                        seen.add(res)

        formats = sorted(formats, key=lambda x: int(x['label'].split('p')[0]))
        return jsonify({'formats': formats})

    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/download', methods=['POST'])
def download():
    url = request.form['url']
    height = request.form.get('format_id', '720')  # Now using resolution
    file_id = str(uuid.uuid4())
    output_path = f"{file_id}.mp4"

    ydl_opts = {
        'outtmpl': output_path,
        'format': f'bestvideo[height<={height}][ext=mp4]+bestaudio[ext=m4a]/best',
        'quiet': True,
        'merge_output_format': 'mp4',
        'retries': 10,
        'socket_timeout': 30,
        'nocheckcertificate': True,
        'cookiefile': 'cookies.txt'

    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
            return "Error: Downloaded file not found or empty", 500

        return send_file(
            output_path,
            as_attachment=True,
            download_name='video.mp4',
            mimetype=mimetypes.guess_type(output_path)[0]
        )

    except Exception as e:
        return f"<h3 style='color:red'>Download failed: {e}</h3>"

    finally:
        def cleanup(path):
            time.sleep(10)
            if os.path.exists(path):
                try:
                    os.remove(path)
                except:
                    pass

        threading.Thread(target=cleanup, args=(output_path,)).start()

if __name__ == '__main__':
    app.run(debug=True)