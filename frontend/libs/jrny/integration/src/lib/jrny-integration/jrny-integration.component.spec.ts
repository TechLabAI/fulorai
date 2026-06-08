import { ComponentFixture, TestBed } from '@angular/core/testing';
import { JrnyIntegrationComponent } from './jrny-integration.component';

describe('JrnyIntegrationComponent', () => {
  let component: JrnyIntegrationComponent;
  let fixture: ComponentFixture<JrnyIntegrationComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [JrnyIntegrationComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(JrnyIntegrationComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
