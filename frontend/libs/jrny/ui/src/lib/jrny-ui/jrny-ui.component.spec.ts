import { ComponentFixture, TestBed } from '@angular/core/testing';
import { JrnyUiComponent } from './jrny-ui.component';

describe('JrnyUiComponent', () => {
  let component: JrnyUiComponent;
  let fixture: ComponentFixture<JrnyUiComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [JrnyUiComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(JrnyUiComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
