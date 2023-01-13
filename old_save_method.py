"""
Function main process
"""
def RunProjector():
  y, size_line, speedRender = 1, 30, 30

  projector = Projector(fullscreensize)

  def update_frame(y, size_line, speedRender):
    projector.canvas.delete("all")
    # projector.canvas.create_rectangle(0,0,projector.screen_width,projector.screen_height, fill="white")
    y += speedRender
    if y + size_line >= projector.screen_height:
      y = 2
    projector.canvas.create_rectangle(1,y,projector.screen_width,y + size_line, fill="white")

    projector.canvas.update_idletasks()
    #projector.canvas.after(10)
    projector.root.after(0, update_frame)

  update_frame(y, size_line, speedRender)

  #projector.root.attributes('-fullscreen', True)
  projector.root.mainloop()
