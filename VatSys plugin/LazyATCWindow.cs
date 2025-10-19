using System;
using System.Net.Http;
using System.Text.Json;
using System.Windows.Forms;
using System.Drawing;
using vatsys;
using VATSYSControls;

namespace LazyATCPlugin
{
    public class LazyATCWindow : BaseForm
    {
        private RadioButton radioRoute;
        private RadioButton radioAltitude;
        private Label departureLabel;
        private TextBox departureBox;
        private Label destinationLabel;
        private TextBox destinationBox;
        private Label altitudeLabel;
        private TextBox altitudeBox;
        private Button fetchButton;
        private ListBox resultsBox;
        private Button preset1Button;
        private Button preset2Button;

        private readonly HttpClient httpClient;

        public LazyATCWindow()
        {
            var handler = new HttpClientHandler { AllowAutoRedirect = true };
            httpClient = new HttpClient(handler);

            Text = "LazyATC";
            Width = 500;
            Height = 550;
            MinimumSize = new Size(500, 400);
            MaximumSize = new Size(800, 600);
            FormBorderStyle = FormBorderStyle.Sizable;
            TopMost = true;

            BackColor = Colours.GetColour(Colours.Identities.WindowBackground);
            ForeColor = Colours.GetColour(Colours.Identities.InteractiveText);
            Font = MMI.eurofont_winsml;

            InitializeControls();
        }

        private void ApplyVatSysStyle(Control control)
        {
            control.BackColor = Colours.GetColour(Colours.Identities.WindowBackground);
            control.ForeColor = Colours.GetColour(Colours.Identities.InteractiveText);
            control.Font = MMI.eurofont_winsml;
        }

        private void InitializeControls()
        {
            radioRoute = new RadioButton { Left = 20, Top = 20, Width = 150, Text = "ROUTE", Checked = true };
            radioAltitude = new RadioButton { Left = 200, Top = 20, Width = 150, Text = "ALT" };
            radioRoute.CheckedChanged += ModeChanged;
            radioAltitude.CheckedChanged += ModeChanged;
            ApplyVatSysStyle(radioRoute);
            ApplyVatSysStyle(radioAltitude);

            departureLabel = new Label { Left = 20, Top = 60, Width = 200, Text = "Departure ICAO:" };
            ApplyVatSysStyle(departureLabel);
            departureBox = new TextBox { Left = 20, Top = 80, Width = 200 };
            ApplyVatSysStyle(departureBox);
            departureBox.KeyDown += Input_KeyDown;

            destinationLabel = new Label { Left = 240, Top = 60, Width = 200, Text = "Destination ICAO:" };
            ApplyVatSysStyle(destinationLabel);
            destinationBox = new TextBox { Left = 240, Top = 80, Width = 200 };
            ApplyVatSysStyle(destinationBox);
            destinationBox.KeyDown += Input_KeyDown;

            altitudeLabel = new Label { Left = 20, Top = 60, Width = 200, Text = "Requested Altitude:" };
            ApplyVatSysStyle(altitudeLabel);
            altitudeBox = new TextBox { Left = 20, Top = 80, Width = 200 };
            ApplyVatSysStyle(altitudeBox);
            altitudeBox.Visible = false;
            altitudeLabel.Visible = false;
            altitudeBox.KeyDown += Input_KeyDown;

            fetchButton = new Button { Left = 20, Top = 120, Width = 150, Text = "Get Valid Options" };
            ApplyVatSysStyle(fetchButton);
            fetchButton.Click += FetchButton_Click;

            preset1Button = new Button { Left = 200, Top = 120, Width = 120, Text = "SY-ML" };
            ApplyVatSysStyle(preset1Button);
            preset1Button.Click += (s, e) => ApplyPreset("YSSY", "YMML", "WOL H65 LEECE Q29 ML", true);

            preset2Button = new Button { Left = 340, Top = 120, Width = 120, Text = "ML-SY" };
            ApplyVatSysStyle(preset2Button);
            preset2Button.Click += (s, e) => ApplyPreset("YMML", "YSSY", "DOSEL Y59 RIVET", false);

            resultsBox = new ListBox { Left = 20, Top = 160, Width = 440, Height = 300 };
            ApplyVatSysStyle(resultsBox);
            resultsBox.KeyDown += ResultsBox_KeyDown;
            resultsBox.DoubleClick += ResultsBox_DoubleClick;

            Controls.Add(radioRoute);
            Controls.Add(radioAltitude);
            Controls.Add(departureLabel);
            Controls.Add(departureBox);
            Controls.Add(destinationLabel);
            Controls.Add(destinationBox);
            Controls.Add(altitudeLabel);
            Controls.Add(altitudeBox);
            Controls.Add(fetchButton);
            Controls.Add(preset1Button);
            Controls.Add(preset2Button);
            Controls.Add(resultsBox);
        }

        private void ApplyPreset(string dep, string dest, string route, bool evenAltitude)
        {
            radioRoute.Checked = true;
            departureBox.Text = dep;
            destinationBox.Text = dest;
            resultsBox.Items.Clear();
            resultsBox.Items.Add($"Any | {route}");

            int baseFL = evenAltitude ? 300 : 310;
            string fl1 = $"FL{baseFL.ToString().PadLeft(3, '0')}";
            string fl2 = $"FL{(baseFL + 20).ToString().PadLeft(3, '0')}";
            resultsBox.Items.Add($"Consider {fl1} or {fl2} instead");
        }

        private void ModeChanged(object sender, EventArgs e)
        {
            bool isRouteMode = radioRoute.Checked;

            departureLabel.Visible = isRouteMode;
            departureBox.Visible = isRouteMode;
            destinationLabel.Visible = isRouteMode;
            destinationBox.Visible = isRouteMode;

            altitudeLabel.Visible = !isRouteMode;
            altitudeBox.Visible = !isRouteMode;
        }

        private async void FetchButton_Click(object sender, EventArgs e)
        {
            resultsBox.Items.Clear();

            try
            {
                if (radioRoute.Checked)
                {
                    string dep = departureBox.Text.Trim().ToUpper();
                    string dest = destinationBox.Text.Trim().ToUpper();

                    if (dep.Length != 4 || dest.Length != 4)
                    {
                        MessageBox.Show("Please enter valid ICAO codes.");
                        return;
                    }

                    string url = $"https://api.pilotassist.dev/routes?dept={dep}&dest={dest}";
                    var response = await httpClient.GetAsync(url);
                    response.EnsureSuccessStatusCode();

                    var json = await response.Content.ReadAsStringAsync();
                    var data = JsonDocument.Parse(json);

                    if (data.RootElement.TryGetProperty("routes", out JsonElement routes))
                    {
                        foreach (var route in routes.EnumerateArray())
                        {
                            string acft = route.TryGetProperty("acft", out JsonElement acftEl) ? acftEl.GetString() ?? "Any" : "Any";
                            string routeText = route.GetProperty("route").GetString();
                            resultsBox.Items.Add($"{acft} | {routeText}");
                        }

                        if (resultsBox.Items.Count == 0)
                        {
                            MessageBox.Show("No valid routes found.");
                        }
                    }
                    else
                    {
                        MessageBox.Show("Unexpected response format.");
                    }
                }
                else
                {
                    string altText = altitudeBox.Text.Trim();
                    if (!int.TryParse(altText, out int filedFL))
                    {
                        MessageBox.Show("Please enter a valid flight level.");
                        return;
                    }

                    string fl1 = $"FL{(filedFL - 10).ToString().PadLeft(3, '0')}";
                    string fl2 = $"FL{(filedFL + 10).ToString().PadLeft(3, '0')}";
                    string suggestion = $"Consider {fl1} or {fl2} instead";

                    resultsBox.Items.Add(suggestion);
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Error fetching data:\n{ex.Message}");
            }
        }

        private void Input_KeyDown(object sender, KeyEventArgs e)
        {
            if (e.KeyCode == Keys.Enter)
            {
                FetchButton_Click(sender, EventArgs.Empty);
                e.SuppressKeyPress = true;
            }
        }

        private void ResultsBox_KeyDown(object sender, KeyEventArgs e)
        {
            if (e.KeyCode == Keys.Enter)
            {
                CopySelectedToClipboard();
                e.SuppressKeyPress = true;
            }
        }

        private void ResultsBox_DoubleClick(object sender, EventArgs e)
        {
            CopySelectedToClipboard();
        }

        private void CopySelectedToClipboard()
        {
            if (resultsBox.SelectedItem == null) return;

            string selected = resultsBox.SelectedItem.ToString();
            string message = "";

            if (radioRoute.Checked)
            {
                int pipeIndex = selected.IndexOf('|');
                string route = pipeIndex >= 0 ? selected.Substring(pipeIndex + 1).Trim() : selected.Trim();
                message = $"Unfortunately your filed route is invalid. Are you able to accept {route}?";
            }
            else
            {
                if (selected.Contains("FL"))
                {
                    var parts = selected.Split(new[] { "FL" }, StringSplitOptions.RemoveEmptyEntries);
                    if (parts.Length >= 2)
                    {
                        string fl1 = parts[0].Trim().Substring(0, 3);
                        string fl2 = parts[1].Trim().Substring(0, 3);
                        message = $"Unfortunately your filed flight level is invalid. Of {fl1} and {fl2}, which would you prefer?";
                    }
                }
            }

            if (!string.IsNullOrEmpty(message))
            {
                Clipboard.SetText(message);
            }
        }
    }
}
