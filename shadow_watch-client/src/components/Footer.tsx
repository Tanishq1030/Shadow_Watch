

const Footer = () => {
  return (
    <footer className="border-t border-border py-8 px-4">
      <div className="container mx-auto">
        <div className="text-center text-sm text-muted-foreground space-y-2">
          <p>
            Built by the Shadow Watch community. The source code is available on{" "}
            <a
              href="https://github.com/Tanishq1030/Shadow_Watch"
              className="text-foreground font-semibold hover:underline"
              target="_blank"
              rel="noopener noreferrer"
            >
              GitHub
            </a>
            . Join our{" "}
            <a
              href="https://discord.com/channels/1460051701389070504/1460051702110748990"
              className="text-foreground font-semibold hover:underline"
              target="_blank"
              rel="noopener noreferrer"
            >
              Discord
            </a>
            {" "}to share feedback!
          </p>
          <p>
            Copyright © 2026-PRESENT{" "}
            <span className="font-medium text-foreground">Tanishq</span>
            . All rights reserved. {" "}
            <span className="ml-2 px-1.5 py-0.5 rounded-full bg-muted border border-border text-[10px] font-mono font-bold">
              v1.0.4
            </span>
          </p>
        </div>
      </div>
    </footer >
  );
};

export default Footer;
