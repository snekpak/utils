from .shell import Shell

class AppShell(Shell):
  
  def run(self):
    self.cmdloop()

  def mount(self, *commanders): # ((cmd,{}), (cmd,{}))
    for commander, opts in commanders:
      self.submount(commander, **opts)
