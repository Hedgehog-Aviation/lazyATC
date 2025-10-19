using System;
using System.ComponentModel.Composition;
using System.Windows.Forms;
using vatsys;
using vatsys.Plugin;

namespace LazyATCPlugin
{
    [Export(typeof(IPlugin))]
    public class LazyATCPlugin : IPlugin
    {
        public string Name => "LazyATC";

        private static CustomToolStripMenuItem LazyATCMenu;
        private static LazyATCWindow LazyATCWindow;

        public LazyATCPlugin()
        {
            LazyATCMenu = new CustomToolStripMenuItem(CustomToolStripMenuItemWindowType.Main, CustomToolStripMenuItemCategory.Tools, new ToolStripMenuItem("LazyATC"));
            LazyATCMenu.Item.Click += LazyATCMenu_Click;
            MMI.AddCustomMenuItem(LazyATCMenu);
        }

        private void LazyATCMenu_Click(object sender, EventArgs e)
        {
            MMI.InvokeOnGUI((MethodInvoker)delegate ()
            {
                if (LazyATCWindow == null || LazyATCWindow.IsDisposed)
                {
                    LazyATCWindow = new LazyATCWindow();
                }
                else if (LazyATCWindow.Visible) return;

                LazyATCWindow.Show();
            });
        }

        public void OnLoad() { }

        public void OnUnload() { }
        public void OnFDRUpdate(FDP2.FDR updated)
        {
            // Not used in this plugin
        }

        public void OnRadarTrackUpdate(RDP.RadarTrack updated)
        {
            // Not used in this plugin
        }
    }
}
