# Author: Reed Graff
# Description: This Add-In for Fusion 360 Enables Users to Generate Patterns Such as Voronoi and Honeycomb Very Easily.
import adsk.core, adsk.fusion, traceback

_app = None
_ui  = None

# Global set of event handlers to keep them referenced for the duration of the command
_handlers = []

def updateSliders(sliderInputs):
    """
    Populate 'slider_configuration' group with as many sliders as set in 'slider_controller'.
    Delete previous ones and create new sliders.
    """
    spinner = sliderInputs.itemById("slider_controller")
    value = spinner.value
    # check ranges
    if value > spinner.maximumValue or value < spinner.minimumValue:
        return

    # delete all sliders we have
    toRemove = []
    for i in range(sliderInputs.count):
        input = sliderInputs.item(i)
        if input.objectType == adsk.core.FloatSliderCommandInput.classType():
            toRemove.append(input)
    
    for input in toRemove:
        input.deleteMe()

    # create new ones with range depending on total number
    for i in range(1, value+1):
        id = str(i)
        sliderInputs.addFloatSliderCommandInput("slider_configuration_" + id, "slider_" + id, "cm", 0, 10.0*value)

# Event handler that reacts to any changes the user makes to any of the command inputs.
class MyCommandInputChangedHandler(adsk.core.InputChangedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            eventArgs = adsk.core.InputChangedEventArgs.cast(args)
            cmdInput = eventArgs.input

            # onInputChange for PatternType
            if cmdInput.id == "PatternType":
                configurationGroup = adsk.core.GroupCommandInput.cast(cmdInput.parentCommandInput)
                configurationInputs = configurationGroup.children
                updateSliders(configurationInputs)
          
        except:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


# Event handler that reacts to when the command is destroyed. This terminates the script.            
class MyCommandDestroyHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            # When the command is done, terminate the script
            # This will release all globals which will remove all event handlers
            adsk.terminate()
        except:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


# Event handler that reacts when the command definitio is executed which
# results in the command being created and this event being fired.
class MyCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            # Get the command that was created.
            cmd = adsk.core.Command.cast(args.command)

            # Connect to the command destroyed event.
            onDestroy = MyCommandDestroyHandler()
            cmd.destroy.add(onDestroy)
            _handlers.append(onDestroy)

            # Connect to the input changed event.           
            onInputChanged = MyCommandInputChangedHandler()
            cmd.inputChanged.add(onInputChanged)
            _handlers.append(onInputChanged)    

            # Get the CommandInputs collection associated with the command.
            inputs = cmd.commandInputs

            # Create a selection input.
            selectionInput = inputs.addSelectionInput('selection', 'Select', 'Basic select command input')
            selectionInput.setSelectionLimits(0)

            # Create dropdown input with radio style.
            dropdownInput3 = inputs.addDropDownCommandInput('PatternType', 'Type of Pattern', adsk.core.DropDownStyles.LabeledIconDropDownStyle);
            dropdown3Items = dropdownInput3.listItems
            dropdown3Items.add('Honeycomb + inset', True, '')
            dropdown3Items.add('Honeycomb', False, '')
            dropdown3Items.add('Voronoi', False, '')
            dropdown3Items.add('Voronoi + inset', False, '')

            # Create value input.
            inputs.addValueInput('value', 'Value', 'cm', adsk.core.ValueInput.createByReal(0.0))
            inputs.addValueInput('value', 'Value', 'cm', adsk.core.ValueInput.createByReal(0.0))

            # Create group
            configurationGroup = inputs.addGroupCommandInput("configuration", "Configuration")
            configurationInputs = configurationGroup.children

            # Create integer spinner input
            configurationInputs.addBoolValueInput('checkbox', 'Checkbox', True, '', False)
        
        except:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


def run(context):
    try:
        global _app, _ui
        _app = adsk.core.Application.get()
        _ui = _app.userInterface

        # Get the existing command definition or create it if it doesn't already exist.
        cmdDef = _ui.commandDefinitions.itemById('PatternGen')
        if not cmdDef:
            cmdDef = _ui.commandDefinitions.addButtonDefinition('PatternGen', 'Pattern Generator', 'This Add-In for Fusion 360 Enables Users to Generate Patterns Such as Voronoi and Honeycomb Very Easily.')

        # Connect to the command created event.
        onCommandCreated = MyCommandCreatedHandler()
        cmdDef.commandCreated.add(onCommandCreated)
        _handlers.append(onCommandCreated)

        # Execute the command definition.
        cmdDef.execute()

        # Prevent this module from being terminated when the script returns, because we are waiting for event handlers to fire.
        adsk.autoTerminate(False)
    except:
        if _ui:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))