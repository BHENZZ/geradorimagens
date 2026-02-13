"""
Configuração dos 6 prompts para geração de imagens de marketplace
Cada prompt é otimizado para um layout específico
"""

def get_prompts_config(produto_nome, beneficios, cor_icones, cor_fonte, cor_destaque, fonte_escolhida):
    """Retorna a configuração dos 6 prompts"""
    
    return [
        # IMAGEM 1: Foto Principal - Produto Isolado
        {
            "tipo": "1_Foto_Principal",
            "descricao": "Produto isolado - Fundo branco puro",
            "prompt": f"""Create a professional high-resolution product photograph.

PRODUCT: {produto_nome}

CRITICAL REQUIREMENTS:
- PURE WHITE background (#FFFFFF) - absolutely nothing else
- Product centered and prominent (takes 60-70% of image)
- Professional studio lighting with soft natural shadows
- Ultra high detail and sharpness - photorealistic
- NO TEXT, NO ICONS, NO GRAPHICS, NO WATERMARKS
- Just the beautiful product itself on pure white
- Premium photography style like Apple, Samsung, or Amazon product photos
- 8K quality, ultra-detailed, catalog quality

Photography style: Professional product photography, studio shot, e-commerce catalog, clean and minimal."""
        },
        
        # IMAGEM 2: Benefício Principal - Layout Lado a Lado
        {
            "tipo": "2_Beneficio_Principal",
            "descricao": "Benefícios à esquerda + Produto à direita",
            "prompt": f"""Create a professional product showcase with side-by-side layout.

PRODUCT: {produto_nome}
MAIN BENEFITS: {chr(10).join(beneficios[:3]) if beneficios else '✓ Premium Quality\\n✓ Modern Design\\n✓ High Performance'}

LAYOUT STRUCTURE (CRITICAL):
LEFT SIDE (60% of image):
- White or subtle gradient background
- Large bold product title at top using {fonte_escolhida} font in {cor_fonte} color
- 3-4 key benefits listed vertically
- Each benefit with a simple geometric LINE ICON in {cor_icones} color
- Medium-sized text in {cor_fonte} color
- Clean spacing between items
- Professional hierarchy

RIGHT SIDE (40% of image):
- Product image prominently displayed
- Product should be clearly visible and attractive
- Subtle shadow or depth effect

FOOTER (bottom of entire image):
- Subtle banner or strip in {cor_destaque} color
- Small trust badge or quality seal
- Can say "PREMIUM QUALITY" or "BESTSELLER" or similar

DESIGN RULES:
- Use {fonte_escolhida} font family style throughout
- Icons: Simple geometric line icons (outline style, not filled)
- Colors: Icons={cor_icones}, Text={cor_fonte}, Accents={cor_destaque}
- CORRECT ENGLISH SPELLING - double check all words
- Clean, professional, modern layout
- High contrast for readability

Style: Modern e-commerce product card, professional marketplace listing"""
        },
        
        # IMAGEM 3: Lista de Usos
        {
            "tipo": "3_Lista_Usos",
            "descricao": "IDEAL PARA: + ícones de uso",
            "prompt": f"""Create a product use cases showcase image.

PRODUCT: {produto_nome}

LAYOUT STRUCTURE:
TOP SECTION:
- Large bold heading "IDEAL FOR:" or "PERFECT FOR:" using {fonte_escolhida} font
- Text in {cor_destaque} color to stand out

CENTER SECTION - VERTICAL LIST OF USE CASES:
- 4-6 use case icons arranged vertically with labels
- Common use cases like: Gym/Fitness, Office/Work, Travel, Home, Sports, Outdoor
- Each with a simple LINE ICON (geometric outline style) in {cor_icones} color
- Short label text next to each icon in {cor_fonte} color
- Clean vertical alignment with good spacing

PRODUCT PLACEMENT:
- Product image on LEFT or RIGHT side (30-40% of image)
- Product clearly visible and attractive
- Can be slightly smaller to emphasize the use cases

ALTERNATIVE LAYOUT (if product doesn't have clear use cases):
- Product on LEFT (40%)
- RIGHT side (60%): Additional benefits with icons not mentioned before
- Title: "MORE BENEFITS" or "ALSO INCLUDES"
- 4-5 extra features with icons listed vertically

DESIGN:
- White or subtle gradient background
- {fonte_escolhida} font family
- Icons in {cor_icones}, text in {cor_fonte}, heading in {cor_destaque}
- CORRECT SPELLING
- Professional and clear

Style: Infographic style, easy to scan, clear visual hierarchy"""
        },
        
        # IMAGEM 4: Produto em Uso
        {
            "tipo": "4_Produto_Uso",
            "descricao": "Produto em uso prático/ambientado",
            "prompt": f"""Create a lifestyle image showing the product in real-world use.

PRODUCT: {produto_nome}

SCENE REQUIREMENTS:
- Show the product being USED in a realistic scenario
- Natural setting appropriate for the product type
- Professional photography style
- Clean, uncluttered background
- Good lighting - natural or studio
- Product should be the clear focus

SCENARIOS TO CONSIDER:
- If it's a bottle/container: person holding it, on a desk, gym setting
- If it's electronics: in use, being charged, with other devices
- If it's clothing/accessories: being worn or displayed naturally
- If it's home goods: in a home setting, kitchen, living room
- If it's sports equipment: in action or ready to use

OVERLAY TEXT (minimal):
- Small subtle text using {fonte_escolhida} font
- Can include short phrase in {cor_destaque} color
- Examples: "IN ACTION", "EVERYDAY USE", "REAL WORLD"
- Text should not dominate - image is primary

STYLE:
- Photorealistic lifestyle photography
- Instagram/Pinterest aesthetic
- Professional but relatable
- Shows product value and usage
- CORRECT SPELLING if any text included

Photography: Lifestyle product photography, real-world context, professional quality"""
        },
        
        # IMAGEM 5: Medidas Técnicas
        {
            "tipo": "5_Medidas_Tecnicas",
            "descricao": "Dimensões com setas",
            "prompt": f"""Create a technical specification image with product dimensions.

PRODUCT: {produto_nome}

LAYOUT:
CENTER:
- Product image shown from best angle to display size
- Product should be clear and detailed
- Clean white or light background

DIMENSION ARROWS:
- Professional measurement arrows (lines with arrow heads)
- Show key dimensions: height, width, depth/diameter
- Arrows in {cor_icones} color
- Clean, technical drawing style
- Labels showing measurements (if known, or placeholders like "24cm", "10cm", "500ml")

LABELS:
- Clear dimension text using {fonte_escolhida} font in {cor_fonte} color
- Can include: "HEIGHT", "WIDTH", "CAPACITY", "DIAMETER"
- Professional technical labels
- Easy to read at any size

ADDITIONAL SPECS (optional small text):
- Weight, capacity, material
- In corner or bottom in small text
- {cor_fonte} color

TITLE (optional):
- "TECHNICAL SPECIFICATIONS" or "DIMENSIONS" at top
- {fonte_escolhida} font in {cor_destaque} color
- Medium size, professional

DESIGN:
- Technical drawing aesthetic
- Clean and precise
- Professional engineering/blueprint style
- {cor_icones} for arrows and lines
- {cor_fonte} for text
- {cor_destaque} for headers
- CORRECT SPELLING

Style: Technical product specification, engineering drawing, professional dimensions display"""
        },
        
        # IMAGEM 6: Garantia Final
        {
            "tipo": "6_Garantia_Final",
            "descricao": "Garantia + Call to Action forte",
            "prompt": f"""Create a powerful final call-to-action image with guarantee.

PRODUCT: {produto_nome}

MAIN MESSAGE (very large, bold):
- "90 DAY GUARANTEE" or "90 DIAS DE GARANTIA" (choose one language)
- OR "MONEY BACK GUARANTEE"
- Use {fonte_escolhida} font family, EXTRA BOLD
- Color: {cor_destaque} (vibrant and eye-catching)
- Should be the DOMINANT element

SECONDARY MESSAGE:
- "IMMEDIATE SHIPPING" or "ENVIO IMEDIATO"
- "FREE RETURNS" or "DEVOLUÇÃO GRÁTIS"
- Medium size text in {cor_fonte} color
- {fonte_escolhida} font family

VISUAL ELEMENTS:
- Large badge/seal/shield shape in background (subtle)
- Gradient or glow effect in {cor_destaque} color
- Simple checkmark or shield ICON in {cor_icones} color
- Professional trust symbols

PRODUCT:
- Small product image in corner or bottom (20-30% of image)
- Or as subtle background element
- Should not compete with text - text is primary

ADDITIONAL TRUST ELEMENTS:
- Small icons for: secure payment, fast shipping, quality guarantee
- Stars or rating symbols in {cor_icones}
- Clean, professional badges

BACKGROUND:
- White or subtle gradient
- Can have decorative geometric shapes in {cor_destaque} (subtle opacity)
- Modern, clean, impactful

OVERALL FEEL:
- BOLD and CONFIDENT
- Creates urgency and trust
- Professional but exciting
- Clear call-to-action energy

Typography: {fonte_escolhida} bold, large sizes
Colors: Dominant {cor_destaque}, accents {cor_icones}, text {cor_fonte}
CORRECT SPELLING - this is critical for trust

Style: Bold marketing image, final CTA, guarantee badge, trust-building, high impact"""
        }
    ]
