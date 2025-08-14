"""
🛒 Arsenal V4 - Module Boutique
==============================

Système de boutique configurable avec ArsenalCoins
"""

import discord
from discord.ext import commands
import sqlite3
from typing import List, Dict, Optional

class ShopModule(commands.Cog):
    """Module boutique pour Arsenal V4"""
    
    def __init__(self, bot):
        self.bot = bot
        self.categories = {
            'roles': '🎭 Rôles',
            'premium': '👑 Premium',
            'cosmetic': '🎨 Cosmétiques',
            'boost': '⚡ Boosts',
            'special': '✨ Spécial'
        }
    
    @commands.group(name='shop', aliases=['boutique'], invoke_without_command=True)
    async def shop(self, ctx, category: str = None):
        """🛒 Boutique Arsenal - Achetez avec vos ArsenalCoins !"""
        
        if category is None:
            await self.show_categories(ctx)
        else:
            await self.show_category_items(ctx, category)
    
    async def show_categories(self, ctx):
        """Afficher les catégories de la boutique"""
        embed = discord.Embed(
            title="🛒 Boutique Arsenal V4",
            description="Utilisez vos ArsenalCoins pour acheter des objets !",
            color=0xf39c12
        )
        
        # Ajouter le solde de l'utilisateur
        user = self.bot.db.get_user(ctx.author.id)
        embed.add_field(
            name="💰 Votre solde",
            value=f"**{user['balance']:,}** ArsenalCoins",
            inline=False
        )
        
        # Ajouter les catégories
        categories_text = ""
        for key, name in self.categories.items():
            item_count = self.get_category_item_count(ctx.guild.id, key)
            categories_text += f"{name} - `!shop {key}` ({item_count} objets)\n"
        
        embed.add_field(
            name="📂 Catégories disponibles",
            value=categories_text,
            inline=False
        )
        
        embed.add_field(
            name="💡 Commandes",
            value="`!shop <catégorie>` - Voir les objets\n`!buy <id>` - Acheter un objet\n`!inventory` - Votre inventaire",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    async def show_category_items(self, ctx, category: str):
        """Afficher les objets d'une catégorie"""
        if category not in self.categories:
            return await ctx.send(f"❌ Catégorie inconnue ! Utilisez: {', '.join(self.categories.keys())}")
        
        items = self.get_shop_items(ctx.guild.id, category)
        
        if not items:
            embed = discord.Embed(
                title=f"🛒 {self.categories[category]}",
                description="Aucun objet disponible dans cette catégorie.",
                color=0xff4757
            )
            return await ctx.send(embed=embed)
        
        embed = discord.Embed(
            title=f"🛒 {self.categories[category]}",
            color=0xf39c12
        )
        
        user = self.bot.db.get_user(ctx.author.id)
        embed.add_field(
            name="💰 Votre solde",
            value=f"**{user['balance']:,}** ArsenalCoins",
            inline=False
        )
        
        for item in items:
            stock_text = f"Stock: {item['stock']}" if item['stock'] != -1 else "Stock: ∞"
            
            embed.add_field(
                name=f"#{item['item_id']} - {item['name']}",
                value=f"{item['description']}\n💰 **{item['price']:,}** AC | {stock_text}",
                inline=False
            )
        
        embed.set_footer(text="Utilisez !buy <id> pour acheter")
        
        await ctx.send(embed=embed)
    
    @commands.command(name='buy', aliases=['acheter'])
    async def buy_item(self, ctx, item_id: int, quantity: int = 1):
        """💳 Acheter un objet de la boutique"""
        
        if quantity <= 0:
            return await ctx.send("❌ La quantité doit être positive !")
        
        # Vérifier si l'objet existe
        item = self.get_shop_item(ctx.guild.id, item_id)
        if not item:
            return await ctx.send(f"❌ Objet #{item_id} introuvable !")
        
        user = self.bot.db.get_user(ctx.author.id)
        total_cost = item['price'] * quantity
        
        # Vérifier le solde
        if user['balance'] < total_cost:
            return await ctx.send(f"❌ Vous n'avez pas assez d'ArsenalCoins ! (Nécessaire: {total_cost:,})")
        
        # Vérifier le stock
        if item['stock'] != -1 and item['stock'] < quantity:
            return await ctx.send(f"❌ Stock insuffisant ! (Disponible: {item['stock']})")
        
        # Traitement de l'achat
        if item['category'] == 'roles':
            success = await self.give_role(ctx, item, quantity)
        else:
            success = await self.add_to_inventory(ctx, item, quantity)
        
        if success:
            # Débiter le compte
            self.bot.db.update_balance(ctx.author.id, -total_cost, f"Shop Purchase: {item['name']}")
            
            # Mettre à jour le stock
            if item['stock'] != -1:
                self.update_item_stock(item['item_id'], -quantity)
            
            embed = discord.Embed(
                title="✅ Achat réussi !",
                description=f"Vous avez acheté **{quantity}x {item['name']}** pour **{total_cost:,}** ArsenalCoins !",
                color=0x00ff41
            )
            
            new_balance = user['balance'] - total_cost
            embed.add_field(name="Nouveau solde", value=f"{new_balance:,} AC", inline=True)
            
            await ctx.send(embed=embed)
        else:
            await ctx.send("❌ Erreur lors de l'achat !")
    
    async def give_role(self, ctx, item: dict, quantity: int) -> bool:
        """Donner un rôle à l'utilisateur"""
        try:
            role = ctx.guild.get_role(item['role_id'])
            if not role:
                await ctx.send(f"❌ Rôle introuvable ! Contactez un administrateur.")
                return False
            
            if role in ctx.author.roles:
                await ctx.send(f"❌ Vous avez déjà le rôle {role.mention} !")
                return False
            
            await ctx.author.add_roles(role)
            await ctx.send(f"🎭 Vous avez reçu le rôle {role.mention} !")
            return True
            
        except discord.Forbidden:
            await ctx.send("❌ Je n'ai pas les permissions pour donner ce rôle !")
            return False
        except Exception as e:
            print(f"Erreur give_role: {e}")
            return False
    
    async def add_to_inventory(self, ctx, item: dict, quantity: int) -> bool:
        """Ajouter un objet à l'inventaire"""
        try:
            with sqlite3.connect(self.bot.db.db_path) as conn:
                cursor = conn.cursor()
                
                # Vérifier si l'objet existe déjà dans l'inventaire
                cursor.execute('''
                    SELECT quantity FROM user_inventory 
                    WHERE user_id = ? AND guild_id = ? AND item_id = ?
                ''', (ctx.author.id, ctx.guild.id, item['item_id']))
                
                existing = cursor.fetchone()
                
                if existing:
                    # Mettre à jour la quantité
                    cursor.execute('''
                        UPDATE user_inventory SET quantity = quantity + ?
                        WHERE user_id = ? AND guild_id = ? AND item_id = ?
                    ''', (quantity, ctx.author.id, ctx.guild.id, item['item_id']))
                else:
                    # Ajouter nouvel objet
                    cursor.execute('''
                        INSERT INTO user_inventory (user_id, guild_id, item_id, quantity)
                        VALUES (?, ?, ?, ?)
                    ''', (ctx.author.id, ctx.guild.id, item['item_id'], quantity))
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"Erreur add_to_inventory: {e}")
            return False
    
    @commands.command(name='inventory', aliases=['inv', 'inventaire'])
    async def inventory(self, ctx, member: discord.Member = None):
        """🎒 Voir votre inventaire"""
        
        target = member or ctx.author
        
        with sqlite3.connect(self.bot.db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT ui.item_id, ui.quantity, si.name, si.description, si.category
                FROM user_inventory ui
                JOIN shop_items si ON ui.item_id = si.item_id
                WHERE ui.user_id = ? AND ui.guild_id = ?
                ORDER BY si.category, si.name
            ''', (target.id, ctx.guild.id))
            
            items = cursor.fetchall()
        
        if not items:
            embed = discord.Embed(
                title=f"🎒 Inventaire de {target.display_name}",
                description="Inventaire vide ! Visitez la boutique avec `!shop`",
                color=0xff4757
            )
            return await ctx.send(embed=embed)
        
        embed = discord.Embed(
            title=f"🎒 Inventaire de {target.display_name}",
            color=0x9b59b6
        )
        
        # Grouper par catégorie
        categories = {}
        for item in items:
            category = item[4]
            if category not in categories:
                categories[category] = []
            categories[category].append(item)
        
        for category, category_items in categories.items():
            category_name = self.categories.get(category, category.title())
            items_text = ""
            
            for item in category_items:
                items_text += f"**{item[2]}** x{item[1]}\n{item[3]}\n\n"
            
            embed.add_field(
                name=f"{category_name}",
                value=items_text,
                inline=False
            )
        
        await ctx.send(embed=embed)
    
    # Commandes d'administration de boutique
    @commands.group(name='shopadmin', invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def shop_admin(self, ctx):
        """🔧 Administration de la boutique"""
        embed = discord.Embed(
            title="🔧 Administration Boutique",
            description="Commandes disponibles:",
            color=0x3498db
        )
        
        embed.add_field(
            name="Ajouter un objet",
            value="`!shopadmin add <catégorie> <prix> <nom> [description]`",
            inline=False
        )
        
        embed.add_field(
            name="Supprimer un objet",
            value="`!shopadmin remove <id>`",
            inline=False
        )
        
        embed.add_field(
            name="Modifier le stock",
            value="`!shopadmin stock <id> <nouveau_stock>`",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    @shop_admin.command(name='add')
    @commands.has_permissions(administrator=True)
    async def add_shop_item(self, ctx, category: str, price: int, name: str, *, description: str = "Aucune description"):
        """Ajouter un objet à la boutique"""
        
        if category not in self.categories:
            return await ctx.send(f"❌ Catégorie invalide ! Utilisez: {', '.join(self.categories.keys())}")
        
        if price <= 0:
            return await ctx.send("❌ Le prix doit être positif !")
        
        with sqlite3.connect(self.bot.db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO shop_items (guild_id, name, description, price, category)
                VALUES (?, ?, ?, ?, ?)
            ''', (ctx.guild.id, name, description, price, category))
            
            item_id = cursor.lastrowid
            conn.commit()
        
        embed = discord.Embed(
            title="✅ Objet ajouté !",
            description=f"**{name}** ajouté à la catégorie {self.categories[category]}",
            color=0x00ff41
        )
        
        embed.add_field(name="ID", value=f"#{item_id}", inline=True)
        embed.add_field(name="Prix", value=f"{price:,} AC", inline=True)
        embed.add_field(name="Description", value=description, inline=False)
        
        await ctx.send(embed=embed)
    
    def get_shop_items(self, guild_id: int, category: str) -> List[Dict]:
        """Récupérer les objets d'une catégorie"""
        with sqlite3.connect(self.bot.db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT item_id, name, description, price, stock, category, role_id
                FROM shop_items
                WHERE guild_id = ? AND category = ?
                ORDER BY price
            ''', (guild_id, category))
            
            items = cursor.fetchall()
            
            return [{
                'item_id': item[0],
                'name': item[1],
                'description': item[2],
                'price': item[3],
                'stock': item[4],
                'category': item[5],
                'role_id': item[6]
            } for item in items]
    
    def get_shop_item(self, guild_id: int, item_id: int) -> Optional[Dict]:
        """Récupérer un objet spécifique"""
        with sqlite3.connect(self.bot.db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT item_id, name, description, price, stock, category, role_id
                FROM shop_items
                WHERE guild_id = ? AND item_id = ?
            ''', (guild_id, item_id))
            
            item = cursor.fetchone()
            
            if item:
                return {
                    'item_id': item[0],
                    'name': item[1],
                    'description': item[2],
                    'price': item[3],
                    'stock': item[4],
                    'category': item[5],
                    'role_id': item[6]
                }
            return None
    
    def get_category_item_count(self, guild_id: int, category: str) -> int:
        """Compter les objets dans une catégorie"""
        with sqlite3.connect(self.bot.db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT COUNT(*) FROM shop_items
                WHERE guild_id = ? AND category = ?
            ''', (guild_id, category))
            
            return cursor.fetchone()[0]
    
    def update_item_stock(self, item_id: int, change: int):
        """Mettre à jour le stock d'un objet"""
        with sqlite3.connect(self.bot.db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE shop_items SET stock = stock + ?
                WHERE item_id = ? AND stock != -1
            ''', (change, item_id))
            conn.commit()

def setup(bot):
    bot.add_cog(ShopModule(bot))
