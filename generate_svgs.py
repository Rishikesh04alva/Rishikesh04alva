import re

def process_file(in_path, out_path, is_light=False):
    with open(in_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replacements
    content = content.replace('Arif Hasan', 'Rishikesh Alva')
    content = content.replace('arifhasan.connect@gmail.com', 'rishikeshalvahere@gmail.com')
    content = content.replace('Full-Stack Developer', 'AI Engineer &amp; Student Dev')
    content = content.replace('Sylhet, Bangladesh', 'Mangalore, Karnataka, India')
    content = content.replace('BSc in CSE', 'B.Tech CSE (AI)')
    content = content.replace('Building + Learning + Shipping', 'AI &bull; Full-Stack &bull; 3D &bull; Creative')
    content = content.replace('VS Code, Git, Android Studio, Figma', 'VS Code, Git, PyTorch, Figma')
    content = content.replace('Dart, C++, Python', 'Python, JavaScript, TypeScript, C++')
    content = content.replace('Flutter', 'React.js, HTML5, CSS3, Tailwind')
    content = content.replace('Node.js', 'Node.js, Express, REST APIs')
    content = content.replace('Firebase, MongoDB', 'MongoDB, MySQL, Firebase')
    content = content.replace('Vercel, Docker, Git', 'Vercel, Netlify, Git, Docker')
    content = content.replace('coming soon', 'rishikeshportfolioforpc.netlify.app')
    content = content.replace('arif-hasan-672249358', 'rishikesh-r-alva-78543a426')
    content = content.replace('Grid.Facebook', 'Grid.Twitter/X')
    content = content.replace('@arifhaxnn', '@AlvaRishihere')
    content = content.replace('@arifhaxn', '@Rishikesh04alva')

    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(content)

process_file('dark_ref.svg', 'dark.svg', is_light=False)
process_file('light_ref.svg', 'light.svg', is_light=True)
print("Regenerated dark.svg and light.svg successfully")
