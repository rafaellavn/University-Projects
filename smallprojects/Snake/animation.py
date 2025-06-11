import snakelib

width = 0  # initialized in play_animation
height = 0  # initialized in play_snake
ui = None  # initialized in play_animation
SPEED = 20
keep_running = True


def draw(x,y,b):
    
    ui.clear()

    ui.place(x,y, b)    
    ui.show()


def play_animation(init_ui):
    global width, height, ui, keep_running
    ui = init_ui
    width, height = ui.board_size()
    x = 0
    y = 0
    snake_body = ui.SNAKE
        
    
    draw(x,y,snake_body)
    while keep_running:
        right_border = width-1
        down_border = height-1
        event = ui.get_event()
        

        if event.name == "alarm":
            if x < right_border:
                x +=1 
                draw(x,y,snake_body)
            elif y == down_border:
                x = 0
                y = 0
                draw(x,y,snake_body)
            else:
                x = 0
                y +=1
                draw(x,y,snake_body)
        elif event.data == "space":
            if snake_body == ui.SNAKE:
                snake_body = ui.FOOD
            else:
                snake_body = ui.SNAKE 
        # make sure you handle the quit event like below,
        # or the test might get stuck in an infinite loop
        elif event.name == "quit":
            keep_running = False


if __name__ == "__main__":
    # do this if running this module directly
    # (not when importing it for the tests)
    ui = snakelib.SnakeUserInterface(4, 4)
    ui.set_animation_speed(SPEED)
    play_animation(ui)
