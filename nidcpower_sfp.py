import nimodinst
import nidcpower
import wx


class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        # begin wxGlade: MyFrame.__init__
        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.SetSize((274, 456))
        self.device_value = wx.ComboBox(self, wx.ID_ANY, choices=[], style=wx.CB_DROPDOWN)  # noqa: E501
        # self.channel_value = wx.SpinCtrlDouble(self, wx.ID_ANY, "0", min=0.0, max=100.0)  # noqa: E501
        self.channel_value = wx.ComboBox(self, wx.ID_ANY, choices=[], style=wx.CB_DROPDOWN)  # noqa: E501
        self.output_function_value = wx.ComboBox(self, wx.ID_ANY, choices=["DC Voltage", "DC Current"], style=wx.CB_DROPDOWN)  # noqa: E501
        self.voltage_value = wx.SpinCtrlDouble(self, wx.ID_ANY, "", min=0.0, max=100.0)  # noqa: E501
        self.current_value = wx.SpinCtrlDouble(self, wx.ID_ANY, "", min=0.0, max=100.0)  # noqa: E501
        self.voltage_range_value = wx.SpinCtrlDouble(self, wx.ID_ANY, "", min=0.0, max=100.0)  # noqa: E501
        self.current_range_value = wx.SpinCtrlDouble(self, wx.ID_ANY, "", min=0.0, max=100.0)  # noqa: E501
        self.output_enabled_value = wx.ToggleButton(self, wx.ID_ANY, "")
        self.voltage_result_value = wx.TextCtrl(self, wx.ID_ANY, "N/A")
        self.current_result_value = wx.TextCtrl(self, wx.ID_ANY, "N/A")
        self.status = wx.StaticText(self, wx.ID_ANY, "Good!")
        self.current_label = wx.StaticText(self, wx.ID_ANY, "Current Limit")
        self.voltage_label = wx.StaticText(self, wx.ID_ANY, "Voltage Level")

        self.__set_properties()
        self.__do_layout()
        # end wxGlade

        self.Bind(wx.EVT_CLOSE, self.__window_close_event)

        # Changing channel, function or device closes and creates new session
        self.Bind(wx.EVT_COMBOBOX, self.__change_device_event, self.device_value)  # noqa: E501
        self.Bind(wx.EVT_COMBOBOX, self.__change_session_event, self.output_function_value)  # noqa: E501
        self.Bind(wx.EVT_COMBOBOX, self.__change_session_event, self.channel_value)  # noqa: E501

        # Changing properties updates reading
        self.Bind(wx.EVT_SPINCTRLDOUBLE, self.__change_attribute_event, self.voltage_value)  # noqa: E501
        self.Bind(wx.EVT_SPINCTRLDOUBLE, self.__change_attribute_event, self.current_value)  # noqa: E501
        self.Bind(wx.EVT_SPINCTRLDOUBLE, self.__change_attribute_event, self.voltage_range_value)  # noqa: E501
        self.Bind(wx.EVT_SPINCTRLDOUBLE, self.__change_attribute_event, self.current_range_value)  # noqa: E501
        self.Bind(wx.EVT_TOGGLEBUTTON, self.__change_attribute_event, self.output_enabled_value)  # noqa: E501

        self._new_device = True
        self._error = False
        self._session = None
        self._modinst_session = None
        self._dev_name = None

        # Using NI-ModInst session to list available NI-DCPower devices
        self._modinst_session = nimodinst.Session('nidcpower')
        for dev in self._modinst_session.devices:
            dev_name = dev.device_name
            self.device_value.Append('{0}'.format(dev_name))
        self.device_value.SetSelection(0)

        # Opening a new session to the selected device
        self.__initialize_new_session()

        # Having a timer to regularly take a reading
        self._timer = wx.Timer(self, wx.ID_ANY)
        self.Bind(wx.EVT_TIMER, self.__take_measurement_event, self._timer)
        self._timer.Start(250)

    def __set_properties(self):
        # begin wxGlade: MyFrame.__set_properties
        self.SetTitle("NI-DCPower Simple SFP")
        self.device_value.SetMinSize((141, 23))
        self.channel_value.SetMinSize((141, 23))
        self.output_function_value.SetMinSize((141, 23))
        self.output_function_value.SetSelection(0)
        self.output_enabled_value.SetMinSize((141, 26))
        self.voltage_result_value.SetMinSize((141, 23))
        self.current_result_value.SetMinSize((141, 23))
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: MyFrame.__do_layout
        entire_frame_sizer = wx.BoxSizer(wx.VERTICAL)
        status_sizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Status"), wx.HORIZONTAL)  # noqa: E501
        current_result_sizer = wx.BoxSizer(wx.HORIZONTAL)
        voltage_result_sizer = wx.BoxSizer(wx.HORIZONTAL)
        output_enabled_sizer = wx.BoxSizer(wx.HORIZONTAL)
        current_range_sizer = wx.BoxSizer(wx.HORIZONTAL)
        voltage_range_sizer = wx.BoxSizer(wx.HORIZONTAL)
        current_sizer = wx.BoxSizer(wx.HORIZONTAL)
        voltage_sizer = wx.BoxSizer(wx.HORIZONTAL)
        output_function_sizer = wx.BoxSizer(wx.HORIZONTAL)
        channel_sizer = wx.BoxSizer(wx.HORIZONTAL)
        device_sizer = wx.BoxSizer(wx.HORIZONTAL)
        device_sizer.Add(self.device_value, 0, 0, 0)
        device_label = wx.StaticText(self, wx.ID_ANY, "Device Name")
        device_sizer.Add(device_label, 0, 0, 0)
        entire_frame_sizer.Add(device_sizer, 1, wx.EXPAND, 0)
        channel_sizer.Add(self.channel_value, 0, 0, 0)
        channel_label = wx.StaticText(self, wx.ID_ANY, "Channel")
        channel_sizer.Add(channel_label, 0, 0, 0)
        entire_frame_sizer.Add(channel_sizer, 1, wx.EXPAND, 0)
        output_function_sizer.Add(self.output_function_value, 0, 0, 0)
        output_function_label = wx.StaticText(self, wx.ID_ANY, "Output Function")  # noqa: E501
        output_function_sizer.Add(output_function_label, 0, 0, 0)
        entire_frame_sizer.Add(output_function_sizer, 1, wx.EXPAND, 0)
        voltage_sizer.Add(self.voltage_value, 0, 0, 0)
        voltage_sizer.Add(self.voltage_label, 0, 0, 0)
        entire_frame_sizer.Add(voltage_sizer, 1, wx.EXPAND, 0)
        current_sizer.Add(self.current_value, 0, 0, 0)
        current_sizer.Add(self.current_label, 0, 0, 0)
        entire_frame_sizer.Add(current_sizer, 1, wx.EXPAND, 0)
        voltage_range_sizer.Add(self.voltage_range_value, 0, 0, 0)
        voltage_range_label = wx.StaticText(self, wx.ID_ANY, "Voltage Range")
        voltage_range_sizer.Add(voltage_range_label, 0, 0, 0)
        entire_frame_sizer.Add(voltage_range_sizer, 1, wx.EXPAND, 0)
        current_range_sizer.Add(self.current_range_value, 0, 0, 0)
        current_range_label = wx.StaticText(self, wx.ID_ANY, "Current Range")
        current_range_sizer.Add(current_range_label, 0, 0, 0)
        entire_frame_sizer.Add(current_range_sizer, 1, wx.EXPAND, 0)
        output_enabled_sizer.Add(self.output_enabled_value, 0, 0, 0)
        output_enabled_label = wx.StaticText(self, wx.ID_ANY, "Output Enabled")
        output_enabled_sizer.Add(output_enabled_label, 0, 0, 0)
        entire_frame_sizer.Add(output_enabled_sizer, 1, wx.EXPAND, 0)
        static_line_1 = wx.StaticLine(self, wx.ID_ANY)
        entire_frame_sizer.Add(static_line_1, 0, wx.EXPAND, 0)
        voltage_result_sizer.Add(self.voltage_result_value, 0, 0, 0)
        voltage_result_label = wx.StaticText(self, wx.ID_ANY, "V")
        voltage_result_sizer.Add(voltage_result_label, 0, 0, 0)
        entire_frame_sizer.Add(voltage_result_sizer, 1, wx.EXPAND, 0)
        current_result_sizer.Add(self.current_result_value, 0, 0, 0)
        current_result_label = wx.StaticText(self, wx.ID_ANY, "A")
        current_result_sizer.Add(current_result_label, 0, 0, 0)
        entire_frame_sizer.Add(current_result_sizer, 1, wx.EXPAND, 0)
        status_sizer.Add(self.status, 0, 0, 0)
        entire_frame_sizer.Add(status_sizer, 25, wx.EXPAND, 0)
        self.SetSizer(entire_frame_sizer)
        self.Layout()
        # end wxGlade

    def __initialize_new_session(self):
        # If opening for the first time set output function and channel
        if self._new_device is True:
            # Open simulated session
            self._session = nidcpower.Session(self.device_value.GetStringSelection(), "", False, "Simulate = 1")  # noqa: E501
            channels = self._session.channel_count
            self._session.close()
            self._session = None

            # Add total channels on device to combo-box
            self.channel_value.Clear()
            for channel in range(channels):
                self.channel_value.Append(str(channel))

            # Set selection to first item in the list
            self.channel_value.SetSelection(0)
            self.output_function_value.SetSelection(0)
            self._new_device = False

        # Open session to device and set controls to default values
        try:
            if self._session is not None:
                self._session.close()
            self._session = nidcpower.Session(self.device_value.GetStringSelection(), self.channel_value.GetStringSelection())  # noqa: E501
            self._session.source_mode = nidcpower.SourceMode.SINGLE_POINT
            if self.output_function_value.GetStringSelection() == "DC Current":
                self._session.output_function = nidcpower.OutputFunction.DC_CURRENT  # noqa: E501
                self.current_label.SetLabel("Current Level")
                self.voltage_label.SetLabel("Voltage Limit")
                self.voltage_value.SetValue(self._session.voltage_limit)
                self.current_value.SetValue(self._session.current_level)
                self.voltage_range_value.SetValue(self._session.voltage_limit_range)  # noqa: E501
                self.current_range_value.SetValue(self._session.current_level_range)  # noqa: E501
            else:
                self._session.output_function = nidcpower.OutputFunction.DC_VOLTAGE  # noqa: E501
                self.current_label.SetLabel("Current Limit")
                self.voltage_label.SetLabel("Voltage Level")
                self.voltage_value.SetValue(self._session.voltage_level)
                self.current_value.SetValue(self._session.current_limit)
                self.voltage_range_value.SetValue(self._session.voltage_level_range)  # noqa: E501
                self.current_range_value.SetValue(self._session.current_limit_range)  # noqa: E501
            self.output_enabled_value.SetValue(False)
            self._session.output_enabled = False
            self._session.source_delay = 0.1
            self._session._initiate()
            self._error = False
            self.status.SetLabel("Good!")

        # Catch error
        except nidcpower.Error as e:
            self._session = None
            self._error = True
            self.status.SetLabel(str(e))
            self.status.Wrap(225)

    def __change_session_event(self, event):
        self.__initialize_new_session()

    def __change_device_event(self, event):
        self._new_device = True
        self.__initialize_new_session()

    def __change_attribute_event(self, event):
        try:
            if self.output_function_value.GetStringSelection() == "DC Current":
                self._session.voltage_limit = self.voltage_value.GetValue()
                self._session.current_level = self.current_value.GetValue()  # noqa: E501
                self._session.voltage_limit_range = self.voltage_range_value.GetValue()  # noqa: E501
                self._session.current_level_range = self.current_range_value.GetValue()  # noqa: E501
            else:
                self._session.voltage_level = self.voltage_value.GetValue()
                self._session.current_limit = self.current_value.GetValue()  # noqa: E501
                self._session.voltage_limit_range = self.voltage_range_value.GetValue()  # noqa: E501
                self._session.current_level_range = self.current_range_value.GetValue()  # noqa: E501
            self._session.output_enabled = self.output_enabled_value.GetValue()  # noqa: E501
            self.status.SetLabel("Good!")
            self._error = False

        except nidcpower.Error as e:
            self._error = True
            self.status.SetLabel(str(e))
            self.status.Wrap(225)

    def __window_close_event(self, event):
        if self._session is not None:
            self._session.close()
        self.Destroy()

    def __take_measurement_event(self, event):
        if self._error is False:
            if self._session is not None:
                try:
                    measurements = self._session.measure_multiple()
                    self.voltage_result_value.SetLabel(str(measurements[0].voltage))  # noqa: E501
                    self.current_result_value.SetLabel(str(measurements[0].current))  # noqa: E501

                except nidcpower.Error as e:
                    self._error = True
                    self.status.SetLabel(str(e))
                    self.status.Wrap(225)
# end of class MyFrame


class MyApp(wx.App):
    def OnInit(self):
        self.frame = MyFrame(None, wx.ID_ANY, "")
        self.SetTopWindow(self.frame)
        self.frame.Show()
        return True
# end of class MyApp


if __name__ == "__main__":
    app = MyApp(0)
    app.MainLoop()
