import noise
import random
import pygame
from settings import BLACK, BLUE, BROWN, GRAY, BROWN, GRASSGREEN, FONT, TILE_SIZE, CHUNK_SIZE, DISPLAY_WIDTH, DISPLAY_HEIGHT, DISPLAY_WIDTH, DISPLAY_HEIGHT, DISPLAY_WIDTH, DISPLAY_HEIGHT, DISPLAY_WIDTH, DISPLAY_HEIGHT
from resources import ITEMS, break_sound, build_sound, background_image, tree_image
from entities import DroppedItem, Particle

class World():
    """
    Generates chunks, handles world edit and related variables
    """
    def __init__(self):
        # modifiers for how fast the algorythm goes through the noise pattern
        self.noise_speed = 0.05
        self.cave_noise_speed = 0.07
        self.cave_noise_multiplier = 30
        
        # game map, format: { "x;y": [[[tilex, tiley], tiletype], [[tilex, tiley], tiletype]] }
        # x;y are chunk (8*8 tiles) coordinates, the chunk is a list containing tiles, which
        # are also lists
        self.game_map = {}
        # spawn location
        self.spawn_x = -100
        self.spawn_y = 0
        # world generation seed
        self.seed = random.randint(-999999, 999999)
        # current biome        
        self.current_biome = 1
        # variables for scrolling the world
        self.scrollx = 0
        self.scrolly = 0
       
        self.current_biome = 1

        # entity lists
        self.mobs = []
        self.worms = []
        self.entities = []
        self.particles = []
        self.popups = []
        self.drops = []
        
    def update(self, mousepos, player):
        # smoothly scroll camera towards the player
        self.scrollx += round((player.rect.centerx-self.scrollx-DISPLAY_WIDTH//2) / 20)
        self.scrolly += round((player.rect.centery-self.scrolly-DISPLAY_HEIGHT//2) / 20)

        self.current_biome = self.get_biome((player.rect.x, player.rect.y))

    def generate_world(self, display):
        # clear lists affected by the world generation loop
        
        self.tiles = []
        self.buildables = []
        self.glows = []
        self.slabs = []
        self.entities = []

        # draw background image
        if self.current_biome == 3:
            display.fill(BLACK)
        else:
            display.blit(background_image, (0, 0))

        # world generation
        for x in range(6):
            for y in range(5):
                # define the target chunk and check if it exists in the game map
                # if so get it else generate it
                target_x = x - 1 + int(round(self.scrollx/(CHUNK_SIZE*TILE_SIZE)))
                target_y = y - 1 + int(round(self.scrolly/(CHUNK_SIZE*TILE_SIZE)))
                target_chunk = str(target_x) + ';' + str(target_y)
                if target_chunk not in self.game_map:
                    self.game_map[target_chunk] = self.generate_chunk(target_x, target_y)
                # go through all tiles in the target chunk
                for tile in self.game_map[target_chunk][0]:
#                    if tile[1] == "torch":
#                        glows.append((tile[0][0]*TILE_SIZE-scrollx-glowradius+TILE_SIZE//2,tile[0][1]*TILE_SIZE-scrolly-glowradius+TILE_SIZE//2))

                    if tile[1] == "slab":
                        self.slabs.append(pygame.Rect(tile[0][0]*TILE_SIZE,
                                                      tile[0][1]*TILE_SIZE,
                                                      TILE_SIZE,
                                                      TILE_SIZE))

                    if tile[1] in ["tree1", "tree2", "tree3", "tree4"]:
                        # drawing trees
                        display.blit(ITEMS[tile[1]]["image"],
                                     (tile[0][0]*TILE_SIZE-self.scrollx-tree_image.get_width() // 2 + 8,
                                      tile[0][1]*TILE_SIZE-self.scrolly-tree_image.get_height()+TILE_SIZE))
                    else:
                        # drawing everything else
                        display.blit(ITEMS[tile[1]]["image"],
                                     (tile[0][0]*TILE_SIZE-self.scrollx,
                                      tile[0][1]*TILE_SIZE-self.scrolly))

                    # mob spawns, when I get around to adding the mob classes
                    # BROKEN CODE, FIX!!
#                    if MOB_SPAWNS:
#                        if tile[1] == "snowy grass":
#                            if random.randint(1, 30000) == 1:
#                                if tile[0][0]*TILE_SIZE < player.rect.x - 100 or tile[0][0]*TILE_SIZE > player.rect.x + 100:
#                                    print("bear spawned, mobs: {}".format(len(mobs)))
#                                    mobs.append(WalkingMob(tile[0][0]*TILE_SIZE, tile[0][1]*TILE_SIZE-48, 1))
#                        if is_night == True:
#                            if tile[1] in ["snowy grass", "grass"]:
#                                if random.randint(1, 10000) == 1:
#                                    if tile[0][0]*TILE_SIZE < player.rect.x - 100 or tile[0][0]*TILE_SIZE > player.rect.x + 100:
#                                        print("skeleton spawned, mobs: {}".format(len(mobs)))
#                                        mobs.append(WalkingMob(tile[0][0]*TILE_SIZE, tile[0][1]*TILE_SIZE-48, 2))
#
                    # physics
                    if tile[1] in ["stone","dirt","grass","snowy grass","plank","rock","coal block","slab"]:
                        self.tiles.append(pygame.Rect(tile[0][0]*TILE_SIZE,
                                                      tile[0][1]*TILE_SIZE,
                                                      TILE_SIZE,
                                                      TILE_SIZE))

                    self.buildables.append(pygame.Rect(tile[0][0]*TILE_SIZE,
                                                       tile[0][1]*TILE_SIZE,
                                                       TILE_SIZE,
                                                       TILE_SIZE))

    def generate_chunk(self, x,y):
        """
        Generates a list of tiles with their coordinates and types using
        the perlin noise algorythm.

        Args:
            x: x chunk coord
            y: y chunk coord
        Returns:
            [[[tilex, tiley], tiletype], [[tilex, tiley], tiletype]]
        """

        # variation in the height differences through an other noise map
        noise_multiplier = (noise.pnoise1((x + self.seed) * 0.01, 
                            repeat=99999999) + 1) * 20
        # heat map for biome generation
        heat_map = int(round(noise.pnoise1((x + self.seed) * 0.01, 
                             repeat=99999999) * noise_multiplier))
        # setting biome based on heat map
        # 1: Forest, 2: Tundra, 3: Underground
        if heat_map < 0:
            biome = 2
        else:
            biome = 1

        chunk_data = [[], biome]
        for x_pos in range(CHUNK_SIZE):
            for y_pos in range(CHUNK_SIZE):
                target_x = x * CHUNK_SIZE + x_pos
                target_y = y * CHUNK_SIZE + y_pos
                tile_type = 0

                plant_map = noise.pnoise1((target_x + self.seed) * 0.4, 
                                           repeat=99999999, persistence=2) * noise_multiplier
                caveheight = int(round(noise.pnoise2((target_x + self.seed) * self.cave_noise_speed, 
                                                     (target_y) * self.cave_noise_speed, 
                                                     repeatx=99999999, repeaty=99999999
                                                     ) * self.cave_noise_multiplier))
                height = int(round(noise.pnoise1((target_x + self.seed) * self.noise_speed, 
                                                 repeat=99999999) * noise_multiplier))

                # cave generation
                if target_y > 29 - height:
                    chunk_data[1] = 3
                    if caveheight < 3:
                        tile_type = "stone"
                        if caveheight < -15:
                            tile_type = "coal block"

                # dirt
                if target_y > 8 - height and target_y < 30 - height:
                    tile_type = "dirt"
                # grass
                elif target_y == 8 - height:
                    if biome == 1:
                        tile_type = "grass"
                    elif biome == 2:
                        tile_type = "snowy grass"

                elif target_y == 7 - height:
                    # plants
                        if plant_map < 0:
                            if biome == 1:
                                tile_type = "plant"
                        # trees
                        if plant_map > 0:
                            if biome == 1:
                                if plant_map < 3:
                                    tile_type = "tree1"
                                elif plant_map < 6:
                                    tile_type = "tree2"
                                elif plant_map < 10:
                                    tile_type = "tree3"
                            elif biome == 2:
                                if 5 < plant_map < 10:
                                    tile_type = "tree4"
                if tile_type != 0:
                    chunk_data[0].append([[target_x,target_y],tile_type])
        return chunk_data

    def get_next_tiles(self, pos):
        """
        Detects if buildable tiles are adjacent to the mouse
        Args:
            pos
        Returns:
            boolean
        """

        testrect = pygame.Rect(0, 0, TILE_SIZE*2, TILE_SIZE*2)
        testrect.centerx = pos[0]
        testrect.centery = pos[1]
        color = BLUE
        for tile in self.buildables:
            if tile.colliderect(testrect):
                return True
        return False

    def remove_tile(self, pos, player, nodrops=False, nodistance=False):
        """
        Removes a tile and by default spawns a drop and particles

        Args:
            pos,
            player,
            nodrops=False,
            nodistance=False
        """
        posx = pos[0]
        posy = pos[1]
        # proceed if the distance between the player and pos is at most 5 tiles
        # or if the nodistance flag is enabled
        if abs(posx - player.rect.centerx) < 5*TILE_SIZE or nodistance and abs(posy - player.rect.centery) < 5*TILE_SIZE or nodistance:
            # get chunk
            chunk = self.get_chunk(pos)
            if chunk != None:
                # loop throught tile in the chunk
                for tile in self.game_map[chunk][0]:
                    tilerect = pygame.Rect(tile[0][0]*TILE_SIZE, tile[0][1]*TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    # if a tile exists at pos remove it
                    if tilerect.collidepoint(posx, posy):
                        self.game_map[chunk][0].remove(tile)
                        # spawn drops if the nodrops flag isn't enabled
                        if not nodrops:
                            if tilerect in self.tiles:
                                self.tiles.remove(tilerect)

                            drop_name = tile[1] 
                            drop_amount = 1
                            # handle exceptions for drops and otherwise just drop the item
                            if tile[1] in ["dirt", "grass", "snowy grass"]:
                                drop_name = "dirt"
                            elif tile[1] in ["stone", "rock"]:
                                drop_name = "rock"
                            elif tile[1] in ["tree1", "tree2", "tree3", "tree4"]:
                                drop_name = "plank",
                                drop_amount = random.randint(5, 15)
                                if tile[1] != "tree4" and random.randint(0, 1) == 1:
                                    self.drops.append(DroppedItem(tilerect.x + 5, tilerect.y + 5,
                                                                  0, 0, "sapling"))
                            elif tile[1] == "coal block":
                                drop_name = "coal"

                            self.drops.append(DroppedItem(tilerect.x + 5,
                                                          tilerect.y + 5,
                                                          0,
                                                          0,
                                                          drop_name))
                       
                            # spawn particles with the color defaulting to brown
                            particle_color = BROWN
                            if tile[1] in ["stone", "rock", "coal block"]:
                                particle_color = GRAY
                            elif tile[1] in ["plant", "grass"]:
                                particle_color = GRASSGREEN
                            for i in range(10):
                                self.particles.append(Particle(tilerect.centerx, 
                                                               tilerect.centery,
                                                               particle_color))
                            # play the breaking sound
                            break_sound.play()
                        break

    def get_chunk(self, pos):
        """
        Get chunk based on coordinates (pos)
        
        Args:
            pos
        Returns:
            chunk or None if no chunk exists
        """
        for chunk in self.game_map.keys():
            # get chunk coordinates from the game_map keys (e.g. 0;0)
            chunkx, chunky = chunk.split(";")
            chunkx = int(chunkx) * TILE_SIZE * CHUNK_SIZE
            chunky = int(chunky) * TILE_SIZE * CHUNK_SIZE
            # create a rect object for the chunk and test for collisions with the mouse
            chunkrect = pygame.Rect(chunkx, chunky, 8*TILE_SIZE, 8*TILE_SIZE)
            if chunkrect.collidepoint(pos[0], pos[1]):
                return chunk

    def tile_exists(self, chunk, x, y):
        """
        Check if tile exists in the game map
        Args:
            chunk, x, y
        Returns:
            tiles or None
        """
        tiles = []
        for tile in self.game_map[chunk][0]:
            if tile[0][0] == x and tile[0][1] == y:
                tiles.append(tile)
        if tiles:
            return tiles

    def place_tile(self, pos, blocktype, inventory, player, item_cost=True):
        """
        Places into a tile based on coordinates
        Args:
            pos, blocktype, inventory, player, item_cost=True
        """
        
        targettile = self.get_tile(pos)
        furniture = False
        if targettile != None:
            # if the target tile is a plant, just remove it and place the tile
            if targettile[1] == "plant":
                self.remove_tile(pos, player)
            # if the target tile is furniture e.g. a wall, torches and other stuff
            # can be placed on it
            elif ITEMS[targettile[1]]["furniture"] == True:
                furniture = True
            # if a tile already exists in the target location, do nothing
                return None 
        posx = pos[0]
        posy = pos[1]
        if abs(posx - player.rect.centerx) < 5*TILE_SIZE \
            and abs(posy - player.rect.centery) < 5*TILE_SIZE:
            chunk = self.get_chunk(pos)
            chunkx, chunky = chunk.split(";")
            # iterate through the chunk and generate rects for collision testing
            for y_pos in range(CHUNK_SIZE):
                for x_pos in range(CHUNK_SIZE):
                    target_x = int(chunkx) * CHUNK_SIZE * TILE_SIZE + x_pos * TILE_SIZE
                    target_y = int(chunky) * CHUNK_SIZE * TILE_SIZE + y_pos * TILE_SIZE
                    tilerect = pygame.Rect(target_x, target_y, TILE_SIZE, TILE_SIZE)
                    
                    if tilerect.collidepoint(posx, posy):
                        target_block = [[target_x // TILE_SIZE, target_y // TILE_SIZE], blocktype]
                        if not self.tile_exists(chunk, target_x // TILE_SIZE,
                                                target_y // TILE_SIZE):
                            if not tilerect.colliderect(player.rect) or furniture == True:
                                self.game_map[chunk][0].append(target_block)
                                build_sound.play()
                                if item_cost:
                                    inventory.remove_item(inventory.equipped, 1)
                        else:
                            if ITEMS[equipped]["furniture"] == True:
                                existing_tiles = self.tile_exists(chunk, target_x // TILE_SIZE, 
                                                                  target_y // TILE_SIZE)
                                if len(existing_tiles) == 1:
                                    blockname = existing_tiles[0][1]
                                    if equipped != blockname:
                                        if blockname == "plank wall":
                                            self.game_map[chunk][0].append(target_block)
                                            build_sound.play()
                                            if item_cost:
                                                inventory.remove_inventory_item(equipped, 1)

    def get_tile(self, pos):
        """
        Gets a tile based on coordinates
        Args:
            pos
        Returns:
            tile or None if no tile is found
        """
        chunk = self.get_chunk(pos)
       
        # loop through the tiles in the chunk, if a tile exists at pos, return it
        tilerect = pygame.Rect(0, 0, TILE_SIZE, TILE_SIZE)
        for tile in self.game_map[chunk][0]:
            tilerect.x = tile[0][0]*TILE_SIZE
            tilerect.y = tile[0][1]*TILE_SIZE
            if tilerect.collidepoint(pos):
                return tile

    def draw_tile_outline(self, pos, equipped, display, player):
        """
        Draws borders around breakable tiles when holding a tool and buildable tiles
        when holding a buildable
        """
        posx = pos[0]
        posy = pos[1]
        if abs(posx - player.rect.centerx) < 5*TILE_SIZE and abs(posy - player.rect.centery) < 5*TILE_SIZE and equipped != "":
            if ITEMS[equipped]["tool"]:
                tile = self.get_tile(pos)
                if tile != None:
                    color = BLACK
                    drawrect = pygame.Rect(tile[0][0]*TILE_SIZE-self.scrollx, tile[0][1]*TILE_SIZE-self.scrolly, TILE_SIZE, TILE_SIZE)
                    #if current_biome == 3 or is_night and color == BLACK:
                    #    color = WHITE
                    pygame.draw.rect(display, color, drawrect, 1)
            elif ITEMS[equipped]["build"]:
                if self.get_next_tiles(pos):
                    chunk = self.get_chunk(pos)
                    chunkx, chunky = chunk.split(";")
                    for y_pos in range(CHUNK_SIZE):
                        for x_pos in range(CHUNK_SIZE):
                            target_x = int(chunkx) * CHUNK_SIZE * TILE_SIZE + x_pos * TILE_SIZE
                            target_y = int(chunky) * CHUNK_SIZE * TILE_SIZE + y_pos * TILE_SIZE
                            tilerect = pygame.Rect(target_x, target_y, TILE_SIZE, TILE_SIZE)
                            if tilerect.collidepoint(posx, posy):
                                tilerect.x -= self.scrollx
                                tilerect.y -= self.scrolly
                                if self.current_biome == 3:
                                    color = WHITE
                                else:
                                    color = BLACK
                                pygame.draw.rect(display, color, tilerect, 1)
 
    def get_biome(self, pos):
        for chunk, chunkdata in self.game_map.items():
            chunkx, chunky = chunk.split(";")
            chunkx = int(chunkx) * TILE_SIZE * CHUNK_SIZE
            chunky = int(chunky) * TILE_SIZE * CHUNK_SIZE
            chunkrect = pygame.Rect(chunkx, chunky, 8*TILE_SIZE, 8*TILE_SIZE)
            if chunkrect.collidepoint(pos[0], pos[1]):
                return chunkdata[1]
