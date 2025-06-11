import snakelib

width = 0  # initialized in play_snake
height = 0  # initialized in play_snake
ui = None  # initialized in play_snake
SPEED = 10
keep_running = True
list_of_points_in_the_snake = [[0,0],[0,1]]
current_position_of_the_apple = (-1,-1)


def play_snake(init_ui):
    global width, height, ui, keep_running, current_position_of_the_apple, list_of_points_in_the_snake

    def determine_apple_position():
        global current_position_of_the_apple 
        global list_of_points_in_the_snake

        l = list_of_points_in_the_snake
        a = [ [0]*width for i in range(height)]
        def create_inital_list(): 
            c = 0
            for i in range(height):
                for j in range(width):
                    if [i,j] not in l:
                        a[i][j] = c
                        c += 1
                    else:
                        a[i][j] = "S"
            return c
        
        def give_correct_corrdinates(n):
            for i in range(height):
                for j in range(width):
                    if a[i][j] == n:
                        return j,i
        current_position_of_the_apple = give_correct_corrdinates(ui.random(create_inital_list()))

    def draw_apple():
        list_of_points_in_the_snake.append([y,x])
        determine_apple_position()
        ui.place(x,y,ui.SNAKE)
        ui.place(current_position_of_the_apple[0], current_position_of_the_apple[1] , ui.FOOD) 
        ui.show() 

    def draw(x,y):
        ui.place(x,y,ui.SNAKE)  

        if [y,x] in list_of_points_in_the_snake and [y,x] != list_of_points_in_the_snake[0]:
            ui.set_game_over()
        elif [y,x] == list_of_points_in_the_snake[0]:
            list_of_points_in_the_snake.append([y,x])
            list_of_points_in_the_snake.pop(0)
        else: 

            list_of_points_in_the_snake.append([y,x])
            ui.place(list_of_points_in_the_snake[0][1],list_of_points_in_the_snake[0][0],ui.EMPTY)
            list_of_points_in_the_snake.pop(0)
            

        ui.show()
        
    ui = init_ui
    width, height = ui.board_size()
    x = 1
    y = 0
 


    determine_apple_position()
    ui.place(0,0,ui.SNAKE)
    ui.place(1,0,ui.SNAKE)

    ui.place(current_position_of_the_apple[0], current_position_of_the_apple[1] , ui.FOOD)
    ui.show() 

    current_direction = "r"
    while keep_running:
        
        event = ui.get_event()
        left_border = 0
        upper_border = 0
        right_border = width-1
        down_border = height-1
        list_of_possible_moves = ["d","u","l","r"]
        if event.name == "alarm":     
            if x < right_border and current_direction == "r":                
                x +=1
                if (x,y) == current_position_of_the_apple:
                    draw_apple()                  
                else: 
                    draw(x,y)
            elif x <= right_border and current_direction =="l" and x != 0:
                x -= 1
                if (x,y) == current_position_of_the_apple:
                    draw_apple()
                else: 
                    draw(x,y)
            elif current_direction == "d" and y != down_border:
                y +=1
                if (x,y) == current_position_of_the_apple:
                    draw_apple() 
                else: 
                    draw(x,y)
            elif current_direction =="u" and y != upper_border:
                y -=1
                if (x,y) == current_position_of_the_apple:
                    draw_apple()
                else: 
                    draw(x,y)
            elif current_direction =="u" and y == upper_border:
                y = down_border
                if (x,y) == current_position_of_the_apple:
                    draw_apple()
                else: 
                    draw(x,y)
            elif current_direction =="d" and y == down_border:
                y = upper_border
                if (x,y) == current_position_of_the_apple:
                    draw_apple()
                else: 
                    draw(x,y)
            elif x == left_border:
                x = right_border
                if (x,y) == current_position_of_the_apple:
                    draw_apple()
                else: 
                    draw(x,y)
            elif x == right_border:
                x = left_border
                if (x,y) == current_position_of_the_apple:
                    draw_apple()
                else: 
                    draw(x,y)
        if event.name == "quit":
            keep_running = False             
        elif event.data in list_of_possible_moves:
                current_direction = event.data

if __name__ == "__main__":
    # do this if running this module directly
    # (not when importing it for the tests)
    ui = snakelib.SnakeUserInterface(20, 20)
    ui.set_animation_speed(SPEED)
    play_snake(ui)
